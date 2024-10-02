'''A class for a virtual network request'''
from VirtualNetwork import VirtualNetwork


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
        self.is_embedded = False
        # flag to indicate if at least one node is embedded (important for step function)
        self.at_least_once = False
        # for FUTURE USE (v2) - weighted VNR according to a formula
        self.weight: float = 0.0
    
    def allocate(self, ) -> None:
    
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
