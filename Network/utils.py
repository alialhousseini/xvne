from VirtualNetwork import VirtualNetwork
from components import VirtualLink, VirtualNode
import random


def create_virtual_network(
    num_virtual_nodes: int = None,
    num_virtual_links: int = None,
    min_node_capacity: int = 10,
    max_node_capacity: int = 100,
    min_link_bandwidth: int = 10,
    max_link_bandwidth: int = 100,
) -> VirtualNetwork:
    '''The main function to create a random virtual network

    Args:
        num_virtual_nodes (int, optional): The number of virtual nodes. Defaults to None.
        num_virtual_links (int, optional): The number of virtual links. Defaults to None.
        If not specified, it will be randomly generated. 

    Returns:
        VirtualNetwork: A virtual network

    '''

    if num_virtual_nodes is None:
        num_virtual_nodes = random.randint(5, 7)

    if num_virtual_links is None:
        num_virtual_links = random.randint(3, 5)

    virtual_network = VirtualNetwork()

    for _ in range(num_virtual_nodes):
        virtual_network.add_virtual_node(VirtualNode(
            random.randint(min_node_capacity, max_node_capacity)))

    for _ in range(num_virtual_links):
        node1, node2 = random.sample(virtual_network.virtual_nodes, 2)
        virtual_network.add_virtual_link(VirtualLink(
            [node1, node2], random.randint(min_link_bandwidth, max_link_bandwidth)))

    return virtual_network


def id_to_str(id: int) -> str:
    return str(id).zfill(2)


def str_to_id(id_str: str) -> int:
    return int(id_str)
