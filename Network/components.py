"""The main components of any network, such as nodes and links."""

# TODO V2.0: MAKE NODES AND LINKS CAPACITIES DYNAMIC FOR REAL-TIME CHANGE

#######################################################################################################
###################################### Basic Network Components #######################################
#######################################################################################################


class Node:
    """A node in the network."""

    _next_id = 0

    def __init__(self, capacity: int) -> None:
        assert capacity > 0, "Capacity must be greater than 0"
        self.id: int = Node._get_next_id()  # incremental id
        self.capacity: int = capacity  # the capacity of the node
        self.available_capacity: int = capacity  # the available capacity of the node
        self.links: list = []  # the links connected to the node in the network
        # the nodes connected by a "direct link"
        self.connected_nodes: list = []

    @classmethod
    def _get_next_id(cls) -> int:
        if not hasattr(cls, '_next_id'):
            cls._next_id = 0
        cls._next_id += 1
        return cls._next_id

    def deduct_capacity(self, amount: int) -> None:
        self.available_capacity -= amount

    def reset_capacity(self) -> None:
        self.available_capacity = self.capacity

    def add_capacity(self, amount: int) -> None:
        assert self.available_capacity + amount <= self.capacity, "Not enough capacity"
        self.available_capacity += amount

    def add_link(self, link: 'Link') -> None:
        self.links.append(link)
        # A link has two nodes, one is self and other node
        # We append the other node
        self.connected_nodes.append(link.get_other_node(self))

    def get_link(self, criterion: str = None) -> 'Link':
        """get one of the links according to a criterion"""
        if criterion is "more_resources":
            max(self.links, key=lambda x: x.available_bandwidth)
        elif criterion is "less_resources":
            min(self.links, key=lambda x: x.available_bandwidth)
        elif criterion is "more_original_resources":
            max(self.links, key=lambda x: x.bandwidth)
        elif criterion is "less_original_resources":
            min(self.links, key=lambda x: x.bandwidth)
        else:
            raise "criterion is not specified"
        return None

    def compare_capacity(self, node: 'Node') -> int:
        if self.capacity > node.capacity:
            return 1
        elif self.capacity < node.capacity:
            return -1
        else:
            return 0

    def __str__(self) -> str:
        return "Node(id=" + str(self.id) + ", cap=" + str(self.capacity) + ")"

    def remove_link(self, link: 'Link') -> None:
        self.links.remove(link)
        self.connected_nodes.remove(link.get_other_node(self))

    def clear_links(self) -> None:
        self.links.clear()
        self.connected_nodes.clear()


class Link:
    """A link in the network."""

    _next_id = 0

    def __init__(self, nodes: list, bandwidth: int) -> None:
        assert bandwidth > 0, "Bandwidth must be greater than 0"
        assert len(nodes) == 2, "Link must have 2 nodes"
        self.id: int = Link._get_next_id()  # incremental id
        self.bandwidth: int = bandwidth  # the bandwidth of the link
        self.available_bandwidth: int = bandwidth  # the available bandwidth of the link
        self.nodes: list = nodes  # the nodes connected to the link
        # store link's info in nodes
        self.nodes[0].add_link(self)
        self.nodes[1].add_link(self)

    @classmethod
    def _get_next_id(cls) -> int:
        if not hasattr(cls, '_next_id'):
            cls._next_id = 0
        cls._next_id += 1
        return cls._next_id

    def decrease_bandwidth(self, amount: int) -> None:
        self.available_bandwidth -= amount

    def __str__(self) -> str:
        return "Link(id=" + str(self.id) + ", bw=" + str(self.bandwidth) + ", Node1=" + str(self.nodes[0]) + ", Node2=" + str(self.nodes[1]) + ")"

    def get_node(self, criterion: str = None) -> 'Node':
        """get one of the extremeties according to a criterion"""
        if criterion is "more_resources":
            return self.nodes[0] if self.nodes[0].available_capacity > self.nodes[1].available_capacity else self.nodes[1]
        elif criterion is "less_resources":
            return self.nodes[0] if self.nodes[0].available_capacity < self.nodes[1].available_capacity else self.nodes[1]
        elif criterion is "more_original_resources":
            return self.nodes[0] if self.nodes[0].capacity > self.nodes[1].capacity else self.nodes[1]
        elif criterion is "less_original_resources":
            return self.nodes[0] if self.nodes[0].capacity < self.nodes[1].capacity else self.nodes[1]
        else:
            raise "criterion is not specified"
        return None

    def get_other_node(self, node: 'Node') -> 'Node':
        return self.nodes[0] if self.nodes[0] is not node else self.nodes[1]

    def compare_bandwidth(self, link: 'Link') -> int:
        if self.bandwidth > link.bandwidth:
            return 1
        elif self.bandwidth < link.bandwidth:
            return -1
        else:
            return 0

    def reset_bandwidth(self) -> None:
        self.available_bandwidth = self.bandwidth

    def add_bandwidth(self, amount: int) -> None:
        assert self.available_bandwidth + amount <= self.bandwidth, "Not enough bandwidth"
        self.available_bandwidth += amount

#######################################################################################################
#################################### Virtual Network Components #######################################
#######################################################################################################


class VirtualNode(Node):
    """A virtual node in the network, it inherits the basic Node class"""

    def __init__(self, capacity: int) -> None:
        super().__init__(capacity)
        # Inherited from Base Class: id, capacity, available_capacity, links, connected_nodes
        # if the node is allocated on a substrate node or not
        self.is_allocated: bool = False
        self.substrate_node: 'SubstrateNode' = None

    def __str__(self) -> str:
        return super().__str__()

    def allocate(self, substrate_node: 'SubstrateNode') -> None:
        """Allocate the virtual node on a substrate node"""
        if not self.is_allocated:
            self.substrate_node = substrate_node
            self.is_allocated = True
            self.deduct_capacity(self.capacity)  # make available capacity 0
            # The controller will handle the substrate node allocation

        else:
            raise "The virtual node is already allocated, release it before allocating"

    def release(self) -> None:
        if self.is_allocated:
            # The controller will handle the substrate node release
            self.reset_capacity()
            self.substrate_node = None
            self.is_allocated = False
        else:
            raise "The virtual node is not allocated"


class VirtualLink(Link):
    """A virtual link in the network, it inherits the basic Link class"""

    def __init__(self, nodes: list, bandwidth: int) -> None:
        super().__init__(nodes, bandwidth)
        # Inherited from Base Class: id, bandwidth, available_bandwidth, nodes
        # PS: A virtual link can be embedded into a path (of several links) in the SN
        # if the link is allocated on a substrate link or not
        self.is_allocated: bool = False
        self.substrate_path: list['SubstrateLink'] = None

    def get_path_length(self) -> int:
        return len(self.substrate_path) if self.substrate_path is not None else 0

    def __str__(self) -> str:
        return super().__str__()

    def allocate(self, substrate_path: list['SubstrateLink'], criterion: str) -> None:
        if not self.is_allocated:
            self.substrate_path = substrate_path
            self.is_allocated = True
            if criterion == 'min':
                minimum_substrate_bandwidth = min(
                    substrate_path, key=lambda x: x.available_bandwidth).available_bandwidth
                self.decrease_bandwidth(minimum_substrate_bandwidth)
                assert self.available_bandwidth == 0, "The bandwidth is not fully allocated"
            else:  # 'sum'
                sum_substrate_bandwidth = sum(
                    [x.available_bandwidth for x in substrate_path])
                self.decrease_bandwidth(sum_substrate_bandwidth)
                assert self.available_bandwidth == 0, "The bandwidth is not fully allocated"
            # For both cases above, the controller will handle the substrate path allocation
        else:
            raise "The virtual link is already allocated, release it before allocating"

    def release(self) -> None:
        if self.is_allocated:
            # The controller will handle the substrate path release
            self.reset_bandwidth()
            self.substrate_path = None
            self.is_allocated = False
        else:
            raise "The virtual link is not allocated"

#######################################################################################################
#################################### Virtual Network Components #######################################
#######################################################################################################


class SubstrateNode(Node):
    """A substrate node in the network, it inherits the basic Node class"""

    def __init__(self, capacity: int) -> None:
        super().__init__(capacity)
        # Inherited from Base Class: id, capacity, available_capacity, links, connected_nodes
        # the list of virtual nodes allocated on this substrate node
        self.allocated_nodes: list['VirtualNode'] = []
        # if the substrate node is occupied or not (at least one allocation)
        self.is_occupied: bool = False

    def __str__(self) -> str:
        return super().__str__()

    def allocate(self, virtual_node: 'VirtualNode') -> None:
        # Additional check
        if self.compare_capacity(virtual_node.capacity) >= 0 and virtual_node.available_capacity != 0:
            if not self.is_occupied:
                self.is_occupied = True
            assert virtual_node not in self.allocated_nodes, "The virtual node is already allocated"
            self.allocated_nodes.append(virtual_node)
            self.deduct_capacity(virtual_node.capacity)
            # The controller will handle the virtual node allocation

    def release(self, virtual_node: 'VirtualNode') -> None:
        if virtual_node in self.allocated_nodes:
            # remove the virtual node from the list of allocated nodes
            self.allocated_nodes.remove(virtual_node)
            self.add_capacity(virtual_node.capacity)  # add the capacity back
            if len(self.allocated_nodes) == 0:
                self.is_occupied = False
            # The controller will handle the virtual node release


class SubstrateLink(Link):
    """A substrate link in the network, it inherits the basic Link class"""

    def __init__(self, nodes: list, bandwidth: int) -> None:
        super().__init__(nodes, bandwidth)
        # Inherited from Base Class: id, bandwidth, available_bandwidth, nodes
        # A substrate link can belong to several paths where on each a virtual link is embedded.
        # The substrate link keeps track of the embedded virtual links
        self.embedded_virtual_links: list['VirtualLink'] = []
        self.is_occupied: bool = False

    def __str__(self) -> str:
        return super().__str__()

    def allocate(self, virtual_link: 'VirtualLink') -> None:
        # Additional check
        if self.compare_bandwidth(virtual_link.bandwidth) >= 0 and virtual_link.available_bandwidth != 0:
            if not self.is_occupied:
                self.is_occupied = True
            assert virtual_link not in self.embedded_virtual_links, "The virtual link is already allocated"
            self.embedded_virtual_links.append(virtual_link)
            self.decrease_bandwidth(virtual_link.bandwidth)
            # The controller will handle the virtual link allocation

    def release(self, virtual_link: 'VirtualLink') -> None:
        if virtual_link in self.embedded_virtual_links:
            # remove the virtual link from the list of embedded virtual links
            self.embedded_virtual_links.remove(virtual_link)
            # add the bandwidth back
            self.add_bandwidth(virtual_link.bandwidth)
            if len(self.embedded_virtual_links) == 0:
                self.is_occupied = False
            # The controller will handle the virtual link release
