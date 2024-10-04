from Networks import VirtualNetworkRequest
from Networks.components import VirtualNode, VirtualLink, SubstrateNode, SubstrateLink, Path


class Event:
    def __init__(self, type: str, time: int, virtual_network_request: VirtualNetworkRequest, **kwargs):
        ''' Generate a list of possible kwargs for the event 
        Args:
            type: the type of event
            time: the time of the event
            virtual_network_request: the virtual network request
            **kwargs: the arguments of the event
        '''
        self.type: str = type
        self.time: int = time
        self.virtual_network_request: VirtualNetworkRequest = virtual_network_request
        self.event_log: str = ""

    def log_event(self, filename: str) -> None:
        with open(filename, 'a') as file:
            file.write(self.event_log)

    def __str__(self) -> str:
        return f"Event(type={self.type}, time={self.time}, virtual_network_request={self.virtual_network_request.id})"


class Arr_Dep_Event(Event):
    def __init__(self, type: str, time: int, virtual_network_request: VirtualNetworkRequest, **kwargs):
        super().__init__(type, time, virtual_network_request, **kwargs)
        if type == 'Arr':
            # the arrival VNR
            self.event_log: str = f"Arrival at time {self.time}, VNR (id:{self.virtual_network_request.id})\n"

        elif type == 'Dep':
            # the departure VNR
            self.event_log: str = f"Departure at time: {self.time}, VNR (id:{self.virtual_network_request.id})\n"
            # This event requires a release, the controller will handle the release

        else:
            raise ValueError("The type of event must be 'Arr' or 'Dep'")

    def __str__(self) -> str:
        return super().__str__()


class FailureEvent(Event):
    def __init__(self, type: str, time: int, virtual_network_request: VirtualNetworkRequest, **kwargs):
        super().__init__(type, time, virtual_network_request, **kwargs)
        if type == 'Node_Failure':
            vnode: VirtualNode = kwargs['vnode']
            snode: SubstrateNode = kwargs['snode']
            # A failure on embedding a node (cap constraint)
            self.event_log: str = f"Node Failure at time {self.time}, VNR(id:{self.virtual_network_request.id}), \
                VNode(id:{vnode.id}, cap:{vnode.available_capacity}), SNode(id:{snode.id}, cap:{snode.available_capacity})\n"

        elif type == 'Link_Failure':
            vlink: VirtualLink = kwargs['vlink']
            spath: Path = kwargs['spath']
            self.event_log = f"Link Failure at time {self.time}, VNR (id:{self.virtual_network_request.id}, \
                VLink(id:{vlink.id}, cap:{vlink.available_bandwidth}), SPath(id:{spath.id}))\n"

        else:
            raise ValueError(
                "The type of event must be 'Node_Failure' or 'Link_Failure'")


class Success_Event(Event):
    def __init__(self, type: str, time: int, virtual_network_request: VirtualNetworkRequest, **kwargs):
        super().__init__(type, time, virtual_network_request, **kwargs)
        if type == 'Node_Success':
            vnode: VirtualNode = kwargs['vnode']
            snode: SubstrateNode = kwargs['snode']
            # A success on embedding a node (cap constraint)
            self.event_log: str = f"Node Successful embedding at time {self.time}, VNR(id:{self.virtual_network_request.id}), \
                VNode(id:{vnode.id}, cap:{vnode.available_capacity}), SNode(id:{snode.id}, cap:{snode.available_capacity})\n"
        elif type == 'Link_Success':
            vlink: VirtualLink = kwargs['vlink']
            spath: Path = kwargs['spath']
            self.event_log = f"Link Successful embedding at time {self.time}, VNR (id:{self.virtual_network_request.id}, \
                VLink(id:{vlink.id}, cap:{vlink.available_bandwidth}), SPath(id:{spath.id}))\n"
        else:
            raise ValueError(
                "The type of event must be 'Node_Success' or 'Link_Success'")
