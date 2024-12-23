from Networks import VirtualNetworkRequest
from Networks.components import VirtualNode, VirtualLink, SubstrateNode, SubstrateLink


class Event:
    def __init__(self, type: str, time: int, vnr: VirtualNetworkRequest, **kwargs):
        ''' Generate a list of possible kwargs for the event 
        Args:
            type: the type of event
            time: the time of the event
            vnr: the virtual network request
            **kwargs: the arguments of the event
        '''
        self.type: str = type
        self.time: int = time
        self.vnr: VirtualNetworkRequest = vnr
        self.event_log: str = ""

    def log_event(self, filename: str) -> None:
        with open(filename, 'a') as file:
            file.write(self.event_log)

    def __str__(self) -> str:
        return f"Event(type={self.type}, time={self.time}, vnr={self.vnr.id})"


class Arr_Dep_Event(Event):
    def __init__(self, type: str, time: int, vnr: VirtualNetworkRequest, **kwargs):
        super().__init__(type, time, vnr, **kwargs)
        if type == 'Arr':
            # the arrival VNR
            self.event_log: str = f"Arrival at time {self.time}, VNR (id:{self.vnr.id})\n"

        elif type == 'Dep':
            # the departure VNR
            self.event_log: str = f"Departure at time: {self.time}, VNR (id:{self.vnr.id})\n"
            # This event requires a release, the controller will handle the release (a release event will be generated)

        else:
            raise ValueError("The type of event must be 'Arr' or 'Dep'")

    def __str__(self) -> str:
        return super().__str__()


class FailureEvent(Event):
    def __init__(self, type: str, time: int, vnr: VirtualNetworkRequest, **kwargs):
        super().__init__(type, time, vnr, **kwargs)
        if type == 'Node_Failure':
            self.vnode: VirtualNode = kwargs['vnode']
            self.snode: SubstrateNode = kwargs['snode']
            self.reason: str = kwargs['reason']
            # reason is either 'cap' constraint violation OR 'already_emb' constraint violation (another node from the same vnr is there)
            self.event_log: str = f"Node Failure at time {self.time}, VNR(id:{self.vnr.id}), VNode(id:{vnode.id}, avl_cap:{vnode.available_capacity}, cap:{vnode.capacity}), SNode(id:{snode.id}, avl_cap:{snode.available_capacity}, cap:{snode.capacity}), Reason:'{reason}'\n"

        elif type == 'Link_Failure':
            vlink: VirtualLink = kwargs['vlink']
            spath: list['SubstrateLink'] = kwargs['spath']
            reason: str = kwargs['reason']
            if spath is None:
                self.event_log = f"Link Failure at time {self.time}, VNR(id:{self.vnr.id}), VLink(id:{vlink.id}, avl_bw:{vlink.available_bandwidth}, bw:{vlink.bandwidth}), Reason:'{reason}'\n"
            else:
                links_info = "["
                for i, path in enumerate(spath):
                    if i == len(spath)-1:
                        links_info += f"SLink(id:{path.id}, avl_bw:{path.available_bandwidth}, bw:{path.bandwidth})]"
                    else:
                        links_info += f"SLink(id:{path.id}, avl_bw:{path.available_bandwidth}, bw:{path.bandwidth}), "
                self.event_log = f"Link Failure at time {self.time}, VNR(id:{self.vnr.id}), VLink(id:{vlink.id}, avl_bw:{vlink.available_bandwidth}, bw:{vlink.bandwidth}), SPath({links_info})\n"

        else:
            raise ValueError(
                "The type of event must be 'Node_Failure' or 'Link_Failure'")


class SuccessEvent(Event):
    def __init__(self, type: str, time: int, vnr: VirtualNetworkRequest, **kwargs):
        super().__init__(type, time, vnr, **kwargs)
        if type == 'Node_Success':
            vnode: VirtualNode = kwargs['vnode']
            snode: SubstrateNode = kwargs['snode']
            # A success on embedding a node (cap constraint)
            self.event_log: str = f"Node Successful embedding at time {self.time}, VNR(id:{self.vnr.id}), VNode(id:{vnode.id}, avl_cap:{vnode.available_capacity}, cap:{vnode.capacity}), SNode(id:{snode.id}, avl_cap:{snode.available_capacity}, cap:{snode.capacity})\n"
        elif type == 'Link_Success':
            vlink: VirtualLink = kwargs['vlink']
            spath: list['SubstrateLink'] = kwargs['spath']
            links_info = "["
            for i, path in enumerate(spath):
                if i == len(spath)-1:
                    links_info += f"SLink(id:{path.id}, avl_bw:{path.available_bandwidth}, bw:{path.bandwidth})]"
                else:
                    links_info += f"SLink(id:{path.id}, avl_bw:{path.available_bandwidth}, bw:{path.bandwidth}), "
            self.event_log = f"Link Successful embedding at time {self.time}, VNR(id:{self.vnr.id}), VLink(id:{vlink.id}, avl_bw:{vlink.available_bandwidth}, bw:{vlink.bandwidth}), SPath({links_info})\n"
        else:
            raise ValueError(
                "The type of event must be 'Node_Success' or 'Link_Success'")


class ReleaseEvent(Event):
    def __init__(self, type: str, time: int, vnr: VirtualNetworkRequest, **kwargs):
        super().__init__(type, time, vnr, **kwargs)
        if type == 'Release':
            # Reason of release is: Either a departure Event or Impossible embedding
            reason: str = kwargs['reason']

            self.event_log: str = f"Release at time {self.time}, VNR(id:{self.vnr.id}), Reason:'{reason}'\n"
        else:
            raise ValueError("The type of event must be 'Release'")
