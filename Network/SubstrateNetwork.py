"""A script that defines the substrate network class"""

from components import SubstrateNode, SubstrateLink, VirtualLink, VirtualNode
import networkx as nx
from matplotlib import pyplot as plt
import random
import json
#######################################################################################################
###################################### Substrate Network ################################################
#######################################################################################################


class SubstrateNetwork:
    """A substrate network"""
    _next_id = 0

    def __init__(self) -> None:
        self.id = SubstrateNetwork.get_next_id()
        self.substrate_nodes: list[SubstrateNode] = []
        self.substrate_links: list[SubstrateLink] = []
        # keep track of all embedded nodes/links on the SN
        # self.embedded_virtual_nodes: list['VirtualNode'] = []
        # self.embedded_virtual_links: list['VirtualLink'] = []

    @classmethod
    def get_next_id(cls) -> int:
        if not hasattr(cls, '_next_id'):
            cls._next_id = 0
        cls._next_id += 1
        return cls._next_id

    def add_substrate_node(self, substrate_node: SubstrateNode) -> None:
        assert substrate_node not in self.substrate_nodes, "The substrate node is already in the substrate network"
        self.substrate_nodes.append(substrate_node)

    def add_substrate_link(self, substrate_link: SubstrateLink) -> None:
        assert substrate_link not in self.substrate_links, "The substrate link is already in the substrate network"
        for node in substrate_link.nodes:
            if node not in self.substrate_nodes:
                self.add_substrate_node(node)
        self.substrate_links.append(substrate_link)

    def remove_substrate_node(self, substrate_node: SubstrateNode) -> None:
        # An occupied node cannot be removed
        assert not substrate_node.is_occupied, "The substrate node is not occupied"
        assert substrate_node in self.substrate_nodes, "The substrate node is not in the substrate network"
        # Removing a substrate node will remove by consequence all its substrate links
        temp_node_links = [
            link for link in self.substrate_links if substrate_node in link.nodes]
        for link in temp_node_links:
            self.substrate_links.remove(link)
        substrate_node.clear_links()
        self.substrate_nodes.remove(substrate_node)

    def remove_substrate_link(self, substrate_link: SubstrateLink) -> None:
        # An occupied link cannot be removed
        assert not substrate_link.is_occupied, "The substrate link is not occupied"
        assert substrate_link in self.substrate_links, "The substrate link is not in the substrate network"
        self.substrate_links.remove(substrate_link)

    def __str__(self) -> str:
        nodes = [str(node) for node in self.substrate_nodes]
        links = [str(link) for link in self.substrate_links]
        return f"SubstrateNetwork(id={self.id}, substrate_nodes={nodes}, substrate_links={links}"

    def get_info(self) -> dict:
        return {
            "id": self.id,
            "substrate_nodes": [str(vn) for vn in self.substrate_nodes],
            "substrate_links": [str(vl) for vl in self.substrate_links]
        }

    def to_json(self, filename: str) -> None:
        network_data = {
            "id": self.id,
            "substrate_nodes": [
                {
                    "id": node.id,
                    "capacity": node.capacity,
                    "available_capacity": node.available_capacity,
                    "is_embedded": node.is_occupied,
                    "allocated_virtual_nodes": [str(vn) for vn in node.allocated_nodes],
                } for node in self.substrate_nodes
            ],
            "substrate_links": [
                {
                    "id": link.id,
                    "bandwidth": link.bandwidth,
                    "available_bandwidth": link.available_bandwidth,
                    "nodes": [str(link.nodes[0]), str(link.nodes[1])],
                    "is_embedded": link.is_occupied,
                    "embedded_virtual_links": [str(vl) for vl in link.embedded_virtual_links],
                } for link in self.substrate_links
            ]
        }

        with open(filename, 'w') as json_file:
            json.dump(network_data, json_file, indent=4)

        print(f"Substrate network saved to {filename}")

    def get_graph(self) -> nx.Graph:
        g = nx.Graph()
        for node in self.substrate_nodes:
            g.add_node(node.id)
        for link in self.substrate_links:
            g.add_edge(link.nodes[0].id, link.nodes[1].id)
        return g

    def draw_graph(self) -> None:
        '''Draw the substrate network graph, using matplotlib, showing all nodes and links'''
        g = self.get_graph()
        pos = nx.spring_layout(g)  # position the nodes using the spring layout

        # Draw the nodes and edges
        nx.draw(g, pos, with_labels=False, node_color="lightblue",
                node_size=800, font_size=10)

        # Draw the node labels (ID and capacity)
        node_labels = {
            node.id: f"ID: {node.id}, cap: {node.capacity}" for node in self.substrate_nodes}
        nx.draw_networkx_labels(g, pos, labels=node_labels, font_size=6)

        # Add edge labels (e.g., bandwidth)
        edge_labels = {(link.nodes[0].id, link.nodes[1].id)                       : f"bw={link.bandwidth}" for link in self.substrate_links}
        nx.draw_networkx_edge_labels(
            g, pos, edge_labels=edge_labels, font_size=6)

        # Show the graph
        plt.show()

    def get_substrate_node(self, node_id: int) -> SubstrateNode:
        for node in self.substrate_nodes:
            if node.id == node_id:
                return node
        return None

    def get_substrate_link(self, link_id: int) -> SubstrateLink:
        for link in self.substrate_links:
            if link.id == link_id:
                return link
        return None


def test_substrate_network():
    # create a substrate network
    substrate_network = SubstrateNetwork()

    # add a set of substrate nodes
    num_substrate_nodes = random.randint(5, 7)
    substrate_nodes = [SubstrateNode(random.randint(1, 10))
                       for n in range(num_substrate_nodes)]

    # add the substrate nodes to the substrate network
    for substrate_node in substrate_nodes:
        substrate_network.add_substrate_node(substrate_node)

    # select 3 pairs of substrate nodes, add a substrate link between them
    for _ in range(3):
        node1, node2 = random.sample(substrate_nodes, 2)
        substrate_network.add_substrate_link(
            SubstrateLink([node1, node2], random.randint(1, 10)))

    # print the substrate network
    print(substrate_network)

    # draw the substrate network
    substrate_network.draw_graph()

    # remove a substrate link and redraw the graph
    candidate_link = substrate_network.substrate_links[0]
    substrate_network.remove_substrate_link(candidate_link)
    substrate_network.draw_graph()

    # remove a substrate node and redraw the graph
    candidate_node = substrate_network.substrate_nodes[0]
    substrate_network.remove_substrate_node(candidate_node)
    substrate_network.draw_graph()

    # check info again
    print(substrate_network)

    return substrate_network


if __name__ == '__main__':
    sn = test_substrate_network()
    sn.to_json('sn.json')
