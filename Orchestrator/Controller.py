'''The GodFather of the scenario'''
from Networks import SubstrateNetwork, VirtualNetworkRequest, VirtualNode, SubstrateNode, VirtualLink, SubstrateLink
from utils import Arr_Dep_Event, FailureEvent, SuccessEvent, ReleaseEvent
from .Recorder import Recorder
from .Evaluator import Evaluator
from .SimulationTime import SimTime


class Controller:
    '''The GodFather of the scenario
        It controls all required components of the scenario.
        It manages the arrival/departure of VNRs
        It manages the failure of VNRs
    '''

    def __init__(self, substrate_network: SubstrateNetwork, vnrs: list[VirtualNetworkRequest]) -> None:
        self.time = SimTime()
        self.substrate_network: SubstrateNetwork = substrate_network
        self.vnrs: list[VirtualNetworkRequest] = vnrs
        # A dict of VNRs, key = VNR id, value = VNR
        # used as a fixed references (for rollback or release)
        self.vnr_dict: dict = {vnr.id: vnr for vnr in vnrs}
        # self.vnrs_embedded: int = 0 - moved to evaluator in v1.3
        # supposing current_time_at_beginning = 0
        # Initilize a recorder to record events
        # The recorder has a list of events to record all events
        self.recorder: Recorder = Recorder('Controller.txt')
        self.evaluator: Evaluator = Evaluator(
            self.vnrs, self.substrate_network)
        self.create_events()  # create arrival and departure events in an ordered list

    def create_events(self) -> None:
        for vnr in self.vnrs:
            self.recorder.add_event(
                Arr_Dep_Event('Arr', vnr.arrival_time, vnr))
        for vnr in self.vnrs:
            self.recorder.add_event(
                Arr_Dep_Event('Dep', vnr.arrival_time + vnr.lifetime, vnr))
        self.recorder.arr_dep_events.sort(key=lambda x: x.time)

    def allocate_node(self, vnode: VirtualNode, snode: SubstrateNode) -> FailureEvent | SuccessEvent | None:
        ''' Allocate a VNode, the process goes as following:
            A step in the RL-ENV is to select the best suitable substrate node.
            The link embedding is a second-stage phenomenon.

            Here, this function receives a VNode and a corresponding SNode
            It starts by checking whether this SNode is already occupied (by any other VNode in the same VNR)
            and it tries to embed VNode in that SNode.
            All records are stored in the corresponding VNR, Vnode, and SNode.
        '''
        # simtime increment
        self.time.tick()
        # Fast check: If the given vnode is already allocated somewhere
        if vnode.is_allocated:
            raise ValueError('VNode is already allocated')

        # Find corresponding VNR, where the VNode is
        for vnr in self.vnrs:
            if vnr.virtual_network.get_virtual_node(vnode.id) is not None:
                corresponding_vnr = vnr
                break
        if vnr is None:
            raise ValueError('VNode is not in any VNR')

        # Check if any other vnode of this VNR is already embedded in the same snode
        # a set of common nodes (if any)
        is_snode_occupied_by_another_vnode = snode.id in corresponding_vnr.nodes_embedded_components.values()
        if not snode.is_occupied and not is_snode_occupied_by_another_vnode:
            # No common nodes, we can start embedding safely
            if snode.available_capacity - vnode.available_capacity >= 0:
                # Embedding is possible (cap constraint is satisfied)
                vnode.allocate(snode)
                snode.allocate(vnode)
                # Add connection record to dict
                corresponding_vnr.nodes_embedded_components[vnode.id] = snode.id
                # check if the VNR has at least one VNode already embedded (important for link embedding)
                if corresponding_vnr.at_least_one:
                    # ---- embed links ----
                    # We try to embed all links between current Vnodes embedded up to now.
                    # If any of them fails, this means that the current configuration of nodes is not the suitable choice
                    # we save temp events to the recorder
                    temp_events = []
                    for link in vnode.links:
                        # A curical condition: both link's nodes have to be allocated in the same substrate node
                        if link.nodes[0].id in corresponding_vnr.nodes_embedded_components.keys() and link.nodes[1].id in corresponding_vnr.nodes_embedded_components.keys():
                            # Iterate through links saved for the just allocated vnode
                            event = self.allocate_link(link, corresponding_vnr)
                            print(event.event_log)
                            if event is not None:  # Additional Redundant check
                                self.recorder.add_event(event)
                                temp_events.append(event)

                    if any(event.type == 'Link_Failure' for event in temp_events):
                        return FailureEvent('Link_Failure', time=self.time.get_time(), vnr=corresponding_vnr, vlink=link, spath=None, reason='Failure during link embedding')

                    # Rollback will be called outside of this function

                else:
                    # Now we have at least one node of this vnr is embedded
                    corresponding_vnr.at_least_one = True

                if corresponding_vnr.is_all_embedded():
                    # The VNR is completely embedded
                    self.evaluator.add_embedded_vnr(corresponding_vnr)

                return SuccessEvent('Node_Success', time=self.time.get_time(), vnr=corresponding_vnr, snode=snode, vnode=vnode)

            else:
                # Embedding is not possible (cap constraint is not satisfied)
                return FailureEvent('Node_Failure', time=self.time.get_time(), vnr=corresponding_vnr, snode=snode, vnode=vnode, reason='cap')

        return FailureEvent('Node_Failure', time=self.time.get_time(), vnr=corresponding_vnr, snode=snode, vnode=vnode, reason='already_emb')

    def allocate_link(self, vlink: VirtualLink, vnr: VirtualNetworkRequest) -> FailureEvent | SuccessEvent:
        ''' A function used inside allocate_node, used for allocating links, if any.
            This function takes into consideration the links made by nodes embedded in allocate_node
            and try to embed them into a path following the shortest K-path method.

            The function starts by looking if there exist any link between any two virtual nodes embedded on SN,
            then it tries to embed that link in a shortest path.

            If the embedding is not possible, it returns a FailureEvent (that informs the Env to rollback changes), otherwise it returns a SuccessEvent
            Note: The embedding follows the default method: (min)
        '''
        # TODO: Time change
        self.time.tick()
        # Retrieve corresponding SNodes (id) for the link's nodes.
        snode1_id: int = vnr.nodes_embedded_components[vlink.nodes[0].id]
        snode2_id: int = vnr.nodes_embedded_components[vlink.nodes[1].id]

        # Get list of paths e.g. [[1,3],[1,4,3],[1,5,2,3]]
        paths = self.substrate_network.get_list_paths(snode1_id, snode2_id)

        if len(paths) == 0:
            # No path exists between these two nodes
            # This means that we have a virtual link, where their nodes are not connected by a path in the subsrate network
            return FailureEvent('Link_Failure', time=self.time.get_time(), vnr=vnr, vlink=vlink, spath=None, reason='no path found')

        # Fast check: If the link is already embedded in any path
        if vlink.is_allocated:
            raise ValueError('Link is already embedded')

        flag = False  # flag to indicate if the link is successfully embedded
        for path in paths:
            # Iterate through paths
            temp_path: list[SubstrateLink] = []
            for i in range(len(path) - 1):
                # Iterate through nodes in the path
                # Check if between two consecutive nodes there is a link
                temp_link: SubstrateLink = self.substrate_network.get_substrate_link_by_nodePair(
                    path[i], path[i+1])
                if temp_link is None:
                    raise ValueError(
                        'Link is not in the substrate network, how is that?')
                else:
                    # There is a link
                    temp_path.append(temp_link)

            # Now I have a list of substrate_links connected to form a path
            # Check if the link is possible to embed
            minimum_band: int = min(
                temp_path, key=lambda x: x.available_bandwidth).available_bandwidth

            if minimum_band - vlink.available_bandwidth >= 0:
                # It is possible to embed!
                vlink.allocate(temp_path)
                for link in temp_path:
                    link.allocate(vlink)
                vnr.links_embedded_components[vlink.id] = [
                    slink.id for slink in temp_path]
                flag = True
                break

        if flag:
            return SuccessEvent('Link_Success', time=self.time.get_time(), vnr=vnr, vlink=vlink, spath=temp_path)

        else:
            return FailureEvent('Link_Failure', time=self.time.get_time(), vnr=vnr, vlink=vlink, spath=None, reason='All paths are not feasible')

    def rollback(self, vnr: VirtualNetworkRequest, reason: str) -> ReleaseEvent:
        ''' Rollback function: Responsible for releasing a VNR and its components'''
        # To release a VNR we follow a down-top approach, i.e we start by releasing nodes and links.
        # Later, we ensure the removal of VNR's data from the substrate network
        # Finally we remove the VNR from the list of VNRs (and all other records related)

        # TODO: Time change
        self.time.tick()

        # Iterate through the dictionary of nodes embedded in the VNR
        for vnode_id, snode_id in vnr.nodes_embedded_components.items():
            # Release the vnode from snode
            self.substrate_network.get_substrate_node(snode_id).release(
                vnr.virtual_network.get_virtual_node(vnode_id))

        # Iterate through the dictionary of links embedded in the VNRs
        for vlink_id, slinks_id in vnr.links_embedded_components.items():
            for slink_id in slinks_id:
                # Release the vlink from slink
                self.substrate_network.get_substrate_link(slink_id).release(
                    vnr.virtual_network.get_virtual_link(vlink_id))

        # Clear embedding info in the VNR, release connections from vnodes and vlinks
        vnr.release()
        vnr.nodes_embedded_components.clear()
        vnr.links_embedded_components.clear()

        return ReleaseEvent('Release', time=self.time.get_time(), vnr=vnr, reason=reason)

    def get_max_num_nodes(self) -> int:
        '''Get the max number of nodes in all VNRs'''
        return max(self.vnrs, key=lambda x: len(x.virtual_network.virtual_nodes))

    def allocate_vnode(self, vnr: VirtualNetworkRequest, snode_id: int) -> FailureEvent | SuccessEvent:
        ''' A function that it selects the first not yet "processed" node '''
        # Iterate through the list of vnode ids
        for vnode_id in vnr.vnodes_id:
            if vnode_id not in vnr.nodes_embedded_components.keys():
                return self.allocate_node(vnr.virtual_network.get_virtual_node(vnode_id), self.substrate_network.get_substrate_node(snode_id))

        return None
