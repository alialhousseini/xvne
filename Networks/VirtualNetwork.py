"""A script that defines the virtual network class"""
from .components import VirtualNode, VirtualLink
import networkx as nx
from matplotlib import pyplot as plt
import random

#######################################################################################################
###################################### Virtual Network ################################################
#######################################################################################################


class VirtualNetwork:
    """A virtual network"""
    _next_id = 0

    def __init__(self) -> None:
        self.id = VirtualNetwork.get_next_id()
        self.virtual_nodes: list[VirtualNode] = []
        self.virtual_links: list[VirtualLink] = []

    @classmethod
    def get_next_id(cls) -> int:
        if not hasattr(cls, '_next_id'):
            cls._next_id = 0
        cls._next_id += 1
        return cls._next_id

    def add_virtual_node(self, virtual_node: VirtualNode) -> None:
        assert virtual_node not in self.virtual_nodes, "The virtual node is already in the virtual network"
        self.virtual_nodes.append(virtual_node)

    def add_virtual_link(self, virtual_link: VirtualLink) -> None:
        assert virtual_link not in self.virtual_links, "The virtual link is already in the virtual network"
        # We cannot add a slink on top of another
        for link in self.virtual_links:
            if link.nodes[0] in virtual_link.nodes and link.nodes[1] in virtual_link.nodes:
                return None
        # Iterate through the Vlink two extremities
        for node in virtual_link.nodes:
            # check whether any of the nodes is already in the virtual network
            if node not in self.virtual_nodes:
                # if not, add it
                self.add_virtual_node(node)
            # If the link is not already in the node info, add it
            if virtual_link not in node.links:
                node.add_link(virtual_link)
        # Add the virtual link
        self.virtual_links.append(virtual_link)

    def remove_virtual_node(self, virtual_node: VirtualNode) -> None:
        assert virtual_node in self.virtual_nodes, "The virtual node is not in the virtual network"
        # Removing a virtual node will remove by consequence all its virtual links
        # get the list of all links connected to the virtual node
        temp_node_links = [
            link for link in self.virtual_links if virtual_node in link.nodes.to_list()]
        # remove the links from the virtual network
        for link in temp_node_links:
            self.virtual_links.remove(link)
        # virtual_node.clear_links() - redundant
        self.virtual_nodes.remove(virtual_node)

    def remove_virtual_link(self, virtual_link: VirtualLink) -> None:
        assert virtual_link in self.virtual_links, "The virtual link is not in the virtual network"
        # Removing a virtual link will remove by consequence the node that become disjoint (VNs are not partitioned) - i.e. degree 1
        # Iterate through the two end-parts of the link
        for node in virtual_link.nodes.to_list():
            # If any of them has a degree of 1, remove it
            if len(node.links) == 1:
                self.remove_virtual_node(node)
            self.virtual_links.remove(virtual_link)

    def __str__(self) -> str:
        nodes = [str(node) for node in self.virtual_nodes]
        links = [str(link) for link in self.virtual_links]
        return f"VirtualNetwork(id={self.id}, virtual_nodes={nodes}, virtual_links={links}"

    def get_info(self) -> dict:
        return {
            "id": self.id,
            "virtual_nodes": [str(vn) for vn in self.virtual_nodes],
            "virtual_links": [str(vl) for vl in self.virtual_links]
        }

    def get_graph(self) -> nx.Graph:
        g = nx.Graph()
        for node in self.virtual_nodes:
            g.add_node(node.id)
        for link in self.virtual_links:
            g.add_edge(link.nodes[0].id, link.nodes[1].id)
        return g

    def draw_graph(self) -> None:
        '''Draw the virtual network graph, using matplotlib, showing all nodes and links'''
        g = self.get_graph()
        pos = nx.spring_layout(g)  # position the nodes using the spring layout

        # Draw the nodes and edges
        nx.draw(g, pos, with_labels=False, node_color="lightblue",
                node_size=800, font_size=10)

        # Draw the node labels (ID and capacity)
        node_labels = {
            node.id: f"ID: {node.id}, cap: {node.capacity}" for node in self.virtual_nodes}
        nx.draw_networkx_labels(g, pos, labels=node_labels, font_size=6)

        # Add edge labels (e.g., bandwidth)
        edge_labels = {(link.nodes[0].id, link.nodes[1].id)
                        : f"bw={link.bandwidth}" for link in self.virtual_links}
        nx.draw_networkx_edge_labels(
            g, pos, edge_labels=edge_labels, font_size=6)

        # Show the graph
        plt.show()

    def get_virtual_node(self, node_id: int) -> VirtualNode:
        for node in self.virtual_nodes:
            if node.id == node_id:
                return node
        return None

    def get_virtual_link(self, link_id: int) -> VirtualLink:
        for link in self.virtual_links:
            if link.id == link_id:
                return link
        return None

    def get_sum_vnode_resources(self, vnode: VirtualNode) -> int:
        vn = self.get_virtual_node(vnode.id)
        return sum([link.bandwidth for link in vn.links]) + vn.capacity

    def get_sum_bws_vnodes(self, vnode: VirtualNode) -> int:
        vn = self.get_virtual_node(vnode.id)
        return sum([link.bandwidth for link in vn.links])

    def get_node_degree(self, vnode: VirtualNode) -> int:
        return len(vnode.links)


def test_virtual_network():
    # create a virtual network
    virtual_network = VirtualNetwork()

    # add a set of virtual nodes
    num_virtual_nodes = 3
    virtual_nodes = [VirtualNode(random.randint(1, 10))
                     for _ in range(num_virtual_nodes)]

    # add the virtual nodes to the virtual network
    for virtual_node in virtual_nodes:
        virtual_network.add_virtual_node(virtual_node)

    # select 3 pairs of virtual nodes, add a virtual link between them
    for _ in range(3):
        node1, node2 = random.sample(virtual_nodes, 2)
        virtual_network.add_virtual_link(
            VirtualLink([node1, node2], random.randint(1, 10)))

    # print the virtual network
    print(virtual_network)

    # draw the virtual network
    virtual_network.draw_graph()

    # remove a virtual link and redraw the graph
    candidate_link = virtual_network.virtual_links[0]
    virtual_network.remove_virtual_link(candidate_link)
    virtual_network.draw_graph()

    # remove a virtual node and redraw the graph
    candidate_node = virtual_network.virtual_nodes[0]
    virtual_network.remove_virtual_node(candidate_node)
    virtual_network.draw_graph()

    # check info again
    print(virtual_network)


if __name__ == '__main__':
    test_virtual_network()
