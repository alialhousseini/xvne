from Networks import SubstrateNetwork, VirtualNetworkRequest, VirtualNetwork
from Networks.components import SubstrateLink, SubstrateNode, VirtualLink, VirtualNode
from Orchestrator import Controller, Recorder
from utils import Event
import random


def main():
    sn = SubstrateNetwork()
    snodes = [SubstrateNode(random.randint(1, 10)) for _ in range(6)]
    slinks = [SubstrateLink(random.sample(snodes, 2),
                            random.randint(1, 10)) for _ in range(6)]
    for snode in snodes:
        sn.add_substrate_node(snode)
    for slink in slinks:
        sn.add_substrate_link(slink)

    vnrs = []
    for _ in range(3):
        vnet = VirtualNetwork()
        vnodes = [VirtualNode(random.randint(1, 10)) for _ in range(3)]
        vlinks = [VirtualLink(random.sample(vnodes, 2),
                              random.randint(1, 10)) for _ in range(3)]
        for vnode in vnodes:
            vnet.add_virtual_node(vnode)
        for vlink in vlinks:
            vnet.add_virtual_link(vlink)
        vnr = VirtualNetworkRequest(vnet, lifetime=random.randint(
            5, 10), arrival_time=random.randint(0, 6))
        vnrs.append(vnr)

    c = Controller(sn, vnrs)
    c.recorder.show_events()


if __name__ == '__main__':
    main()
