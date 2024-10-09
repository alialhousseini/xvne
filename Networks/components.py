"""The main components of any network, such as nodes and links."""

# TODO V2.0: MAKE NODES AND LINKS CAPACITIES DYNAMIC FOR REAL-TIME CHANGE

#######################################################################################################
###################################### Basic Network Components #######################################
#######################################################################################################


class Node:
    """
    A node in the network.

    Parameters:
        capacity (int): the capacity of the node

    Attributes:
        id (int): the id of the node
        capacity (int): the capacity of the node
        available_capacity (int): the available capacity of the node
        links (list[Link]): the links connected to the node in the network
        connected_nodes (list[Node]): the nodes connected by a "direct link"
    """

    _next_id = 0

    def __init__(self, capacity: int) -> None:
        assert capacity > 0, "Capacity must be greater than 0"
        self.id: int = Node._get_next_id()  # incremental id
        self.capacity: int = capacity  # the capacity of the node
        self.available_capacity: int = capacity  # the available capacity of the node
        # the links connected to the node in the network
        self.links: list[Link] = []
        # the nodes connected by a "direct link"
        self.connected_nodes: list[Node] = []

    @classmethod
    def _get_next_id(cls) -> int:
        if not hasattr(cls, '_next_id'):
            cls._next_id = 0
        cls._next_id += 1
        return cls._next_id

    def deduct_capacity(self, amount: int) -> None:
        '''Deduct the amount of capacity from the node'''
        assert self.available_capacity >= amount, "Not enough available capacity"
        self.available_capacity -= amount

    def reset_capacity(self) -> None:
        '''Reset the capacity of the node'''
        self.available_capacity = self.capacity

    def add_capacity(self, amount: int) -> None:
        '''Add the amount of capacity to the node'''
        assert self.available_capacity + amount <= self.capacity, "Not enough capacity"
        self.available_capacity += amount

    def add_link(self, link: 'Link') -> None:
        '''Add a link to the node'''
        self.links.append(link)
        # A link has two nodes, one is self and other node
        # We append the other node
        self.connected_nodes.append(link.get_other_node(self))

    def get_link(self, criterion: str = None) -> 'Link':
        """get one of the links according to a criterion"""
        if criterion == "more_resources":
            max(self.links, key=lambda x: x.available_bandwidth)
        elif criterion == "less_resources":
            min(self.links, key=lambda x: x.available_bandwidth)
        elif criterion == "more_original_resources":
            max(self.links, key=lambda x: x.bandwidth)
        elif criterion == "less_original_resources":
            min(self.links, key=lambda x: x.bandwidth)
        else:
            raise "criterion is not specified"
        return None

    def __str__(self) -> str:
        return "Node(id=" + str(self.id) + ", cap=" + str(self.capacity) + ")"

    def remove_link(self, link: 'Link') -> None:
        '''Remove a link from the node'''
        self.links.remove(link)
        self.connected_nodes.remove(link.get_other_node(self))

    def clear_links(self) -> None:
        '''Remove all links from the node'''
        self.links.clear()
        self.connected_nodes.clear()

    def __eq__(self, other):
        '''Compare two nodes by their id'''
        if isinstance(other, Node):
            return self.id == other.id
        return False

    def __hash__(self):
        """Return the hash of the node, which is the hash of its id."""
        return hash(self.id)


class NodePair:
    '''
    A pair of nodes in the network.

    Parameters:
        node1 (Node): the first node
        node2 (Node): the second node

    Attributes:
        first (int): the id of the first node
        second (int): the id of the second node
        node1 (Node): the first node
        node2 (Node): the second node

    Used for defining a link: link = Link(node1, node2)
    '''

    def __init__(self, node1: 'Node', node2: 'Node') -> None:
        self.first, self.second = sorted((node1.id, node2.id))
        self.node1 = node1 if node1.id == self.first else node2
        self.node2 = node2 if node2.id == self.second else node1

    def __repr__(self):
        return f"({self.first}, {self.second})"

    def __eq__(self, other):
        return (self.first, self.second) == (other.first, other.second)

    def __hash__(self):
        return hash((self.first, self.second))

    def __getitem__(self, id: int) -> Node:
        if id == 0:
            return self.node1
        elif id == 1:
            return self.node2
        else:
            return None

    def __iter__(self):
        return iter([self.node1, self.node2])


class Link:
    """
    A link in the network.

    Parameters:
        nodes (list): the nodes connected to the link
        bandwidth (int): the bandwidth of the link

    Attributes:
        id (int): the id of the link
        bandwidth (int): the bandwidth of the link
        available_bandwidth (int): the available bandwidth of the link
        nodes (NodePair): the nodes connected to the link
    """

    _next_id = 0

    def __init__(self, nodes: list, bandwidth: int) -> None:
        assert bandwidth > 0, "Bandwidth must be greater than 0"
        assert len(nodes) == 2, "Link must have 2 nodes"
        self.id: int = Link._get_next_id()  # incremental id
        self.bandwidth: int = bandwidth  # the bandwidth of the link
        self.available_bandwidth: int = bandwidth  # the available bandwidth of the link
        # the nodes connected to the link
        self.nodes: NodePair = NodePair(nodes[0], nodes[1])
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
        '''Decrease the amount of bandwidth from the link'''
        self.available_bandwidth -= amount

    def __str__(self) -> str:
        return "Link(id=" + str(self.id) + ", bw=" + str(self.bandwidth) + ", Node1=" + str(self.nodes[0]) + ", Node2=" + str(self.nodes[1]) + ")"

    def get_node(self, criterion: str = None) -> 'Node':
        """get one of the extremeties according to a criterion"""
        if criterion == "more_resources":
            return self.nodes[0] if self.nodes[0].available_capacity > self.nodes[1].available_capacity else self.nodes[1]
        elif criterion == "less_resources":
            return self.nodes[0] if self.nodes[0].available_capacity < self.nodes[1].available_capacity else self.nodes[1]
        elif criterion == "more_original_resources":
            return self.nodes[0] if self.nodes[0].capacity > self.nodes[1].capacity else self.nodes[1]
        elif criterion == "less_original_resources":
            return self.nodes[0] if self.nodes[0].capacity < self.nodes[1].capacity else self.nodes[1]
        else:
            raise "criterion is not specified"

    def get_other_node(self, node: 'Node') -> 'Node':
        '''Get the other node in the link'''
        return self.nodes[0] if self.nodes[0] is not node else self.nodes[1]

    def reset_bandwidth(self) -> None:
        '''Reset the bandwidth of the link'''
        self.available_bandwidth = self.bandwidth

    def add_bandwidth(self, amount: int) -> None:
        '''Add the amount of bandwidth to the link'''
        assert self.available_bandwidth + amount <= self.bandwidth, "Not enough bandwidth"
        self.available_bandwidth += amount


# Tested and works, while not required for this version.
# class Path:
#     _next_id = 0

#     def __init__(self, substrate_links: list['SubstrateLink']) -> None:
#         self.id = Path.get_next_id()
#         self.substrate_links = substrate_links
#         self.virtual_links = []  # each element is a virtual link

#     def __len__(self) -> int:
#         return len(self.substrate_links)

#     @classmethod
#     def get_next_id(cls) -> int:
#         if not hasattr(cls, '_next_id'):
#             cls._next_id = 0
#         cls._next_id += 1
#         return cls._next_id

#     def embed(self, virtual_link: 'VirtualLink') -> None:
#         self.virtual_links.append(virtual_link)
#         for slink in self.substrate_links:
#             slink.allocate(virtual_link)

#     def __str__(self) -> str:
#         return "Path(id=" + str(self.id) + ", slinks=" + str(self.substrate_links) + ", vlinks=" + str(self.virtual_links) + ")"

#     def list_of_nodes(self) -> list:
#         nodes = []
#         for link in self.substrate_links:
#             nodes.append(link.nodes[0].id)
#             nodes.append(link.nodes[1].id)
#         return list(set(nodes))

#     def release(self, vlink: 'VirtualLink') -> None:
#         if vlink not in self.virtual_links:
#             raise "The virtual link is not in the path"
#         else:
#             for slink in self.substrate_links:
#                 # slink.embedded_virtual_links.remove(vlink) - redundant
#                 slink.release(vlink)
#             self.virtual_links.remove(vlink)


#######################################################################################################
#################################### Virtual Network Components #######################################
#######################################################################################################


class VirtualNode(Node):
    """
    A virtual node in the network, it inherits the basic Node class
    """

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
        '''Release the virtual node from the substrate node'''
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
        self.substrate_path: list['SubstrateLink'] = []

    def get_path_length(self) -> int:
        return len(self.substrate_path)

    def __str__(self) -> str:
        return super().__str__()

    def allocate(self, substrate_path: list['SubstrateLink'], criterion: str = 'min') -> None:
        if not self.is_allocated:  # and substrate_path is None - redundant
            self.substrate_path = substrate_path
            self.is_allocated = True
            # TODO: V2.0 - MIN for demand and SUM for bandwidth
            if criterion == 'min':
                minimum_substrate_bandwidth = min(
                    substrate_path, key=lambda x: x.available_bandwidth).available_bandwidth
                self.decrease_bandwidth(self.bandwidth)

            else:  # 'sum'
                sum_substrate_bandwidth = sum(
                    [x.available_bandwidth for x in substrate_path])
                self.decrease_bandwidth(self.bandwidth)

            # For both cases above, the controller will handle the substrate path allocation
        else:
            raise "The virtual link is already allocated, release it before allocating"

    def release(self) -> None:
        if self.is_allocated:
            # The controller will handle the substrate path release
            self.reset_bandwidth()
            self.substrate_path = []
            self.is_allocated = False
        else:
            raise "The virtual link is not allocated"

#######################################################################################################
#################################### Substrate Network Components #######################################
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
        if self.available_capacity - virtual_node.capacity >= 0:
            if not self.is_occupied:
                self.is_occupied = True
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
        if self.available_bandwidth - virtual_link.bandwidth >= 0:
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
