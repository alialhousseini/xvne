'''A class for a virtual network request'''
from time import time
from .VirtualNetwork import VirtualNetwork


class VirtualNetworkRequest:
    '''A class for a virtual network request'''
    _next_id = 0

    def __init__(self, virtual_network: VirtualNetwork, lifetime: int, arrival_time: int) -> None:
        self.id = VirtualNetworkRequest.get_next_id()
        assert lifetime > 0, "lifetime must be a positive integer"
        assert arrival_time >= 0, "arrival_time must be a non-negative integer"

        self.virtual_network = virtual_network
        self.lifetime = lifetime
        self.arrival_time = arrival_time
        # flag to indicate if the request is embedded (as a whole)
        # turned on when all (nodes+links) are successfully embedded
        self.is_embedded = False
        # flag to indicate if at least one node is embedded (important for step function - to embed links)
        self.at_least_one = False
        # for FUTURE USE (v2) - weighted VNR according to a formula
        self.weight: float = 0.0
        self.nodes_embedded_components: dict = {}  # key = vnode id, value = snode id
        self.links_embedded_components: dict = {}  # key = link id, value = spath id

    # def allocate_vnode(self, virtual_node: VirtualNode, substrate_node: SubstrateNode) -> Event:
    #     if not virtual_node.is_allocated:
    #         if virtual_node.available_capacity <= substrate_node.available_capacity:
    #             # Can be embedded (vnode is not yet embedded and cap constraint is respected)
    #             virtual_node.allocate(substrate_node)
    #             # Record the embedding (by ids)
    #             self.embedded_components[virtual_node.id] = substrate_node.id
    #             return Event('successful_node_embedding',
    #                          virtual_network_request=self,
    #                          time=time(),
    #                          virtual_node=virtual_node,
    #                          substrate_node=substrate_node)
    #         else:
    #             # Cannot be embedded (cap constraint is not respected)
    #             return Event('Fail', sub_type='node_cap', time=time(), virtual_network_request=self, snode=substrate_node, vnode=virtual_node)
    #     else:
    #         # Record a non logical error
    #         return Event('Error', time=time(), virtual_network_request=self)

    @classmethod
    def get_next_id(cls) -> int:
        if not hasattr(cls, '_next_id'):
            cls._next_id = 0
        cls._next_id += 1
        return cls._next_id

    def get_virtual_network(self) -> VirtualNetwork:
        return self.virtual_network

    def get_lifetime(self) -> int:
        return self.lifetime

    def get_arrival_time(self) -> int:
        return self.arrival_time

    def __str__(self) -> str:
        return f"VirtualNetworkRequest(virtual_network={self.virtual_network}, lifetime={self.lifetime}, arrival_time={self.arrival_time})"
