'''A class for a virtual network request'''
from time import time
from .VirtualNetwork import VirtualNetwork


class VirtualNetworkRequest:
    '''
    A class for a virtual network request
    
    Attributes:
        id (int): The unique id of the virtual network request
        virtual_network (VirtualNetwork): The virtual network
        lifetime (int): The lifetime of the virtual network request
        arrival_time (int): The arrival time of the virtual network request
        at_least_one (bool): Flag to indicate if at least one node is embedded
        weight (float): For FUTURE USE (v2) - weighted VNR according to a formula
        nodes_embedded_components (dict): key = vnode id, value = snode id
        links_embedded_components (dict): key = link id, value = list of vlinks_id
        vnodes_id (list): list of vnode ids
    '''
    _next_id = 0

    def __init__(self, virtual_network: VirtualNetwork, lifetime: int, arrival_time: int) -> None:
        self.id = VirtualNetworkRequest.get_next_id()
        assert lifetime > 0, "lifetime must be a positive integer"
        assert arrival_time >= 0, "arrival_time must be a non-negative integer"

        self.virtual_network = virtual_network
        self.lifetime = lifetime
        self.arrival_time = arrival_time
        # flag to indicate if at least one node is embedded (important for step function - to embed links)
        self.at_least_one = False
        # for FUTURE USE (v2) - weighted VNR according to a formula
        self.weight: float = 0.0
        self.nodes_embedded_components: dict = {}  # key = vnode id, value = snode id
        # key = link id, value = list of vlinks_id
        self.links_embedded_components: dict = {}
        # list of vnode ids
        self.vnodes_id: list = list(
            map(lambda x: x.id, self.virtual_network.virtual_nodes))

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

    def is_all_embedded(self) -> bool:
        for node in self.virtual_network.virtual_nodes:
            if not node.is_allocated:
                return False
        for link in self.virtual_network.virtual_links:
            if not link.is_allocated:
                return False
        return True

    def release(self) -> None:
        for node in self.virtual_network.virtual_nodes:
            if node.is_allocated:
                node.release()
        for link in self.virtual_network.virtual_links:
            if link.is_allocated:
                link.release()

    def get_sum_all_resources(self) -> int:
        sum = 0
        for node in self.virtual_network.virtual_nodes:
            sum += node.capacity
        for link in self.virtual_network.virtual_links:
            sum += link.bandwidth
        return sum
