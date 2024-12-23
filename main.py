from Networks import SubstrateNetwork, VirtualNetworkRequest, VirtualNetwork
from Networks.components import SubstrateLink, SubstrateNode, VirtualLink, VirtualNode
from Orchestrator import Controller, Recorder
from Environment import VNEEnvironment
from utils import Event
import random
from stable_baselines3.common import env_checker


def main():
    sn: SubstrateNetwork = SubstrateNetwork()

    # snodes
    snode1 = SubstrateNode(7)
    snode2 = SubstrateNode(9)
    snode3 = SubstrateNode(6)
    snode4 = SubstrateNode(9)
    snodes = [snode1, snode2, snode3, snode4]

    # slinks
    slink1 = SubstrateLink([snode1, snode2], 4)
    slink2 = SubstrateLink([snode2, snode3], 3)
    slink3 = SubstrateLink([snode3, snode4], 5)
    slink4 = SubstrateLink([snode2, snode4], 5)
    slink5 = SubstrateLink([snode4, snode1], 9)
    slinks = [slink1, slink2, slink3, slink4, slink5]

    for snode in snodes:
        sn.add_substrate_node(snode)
    for slink in slinks:
        sn.add_substrate_link(slink)

    # vnodes
    vnode1 = VirtualNode(3)
    vnode2 = VirtualNode(7)
    vnode3 = VirtualNode(4)
    # temp
    vnodes = [vnode1, vnode2, vnode3]

    # vlinks
    vlink1 = VirtualLink([vnode1, vnode2], 1)
    vlink2 = VirtualLink([vnode2, vnode3], 5)
    vlinks = [vlink1, vlink2]

    vn = VirtualNetwork()
    for vnode in vnodes:
        vn.add_virtual_node(vnode)
    for vlink in vlinks:
        vn.add_virtual_link(vlink)

    # vnr
    vnr = VirtualNetworkRequest(vn, arrival_time=1, lifetime=10)

    # controller
    c = Controller(sn, [vnr])

    # event1 = c.allocate_node(vnode1, snode1)
    # print(event1.event_log)
    # event2 = c.allocate_node(vnode2, snode2)
    # print(event2.event_log)
    # event3 = c.allocate_node(vnode3, snode4)
    # print(event3.event_log)

    # print(vnr.nodes_embedded_components)
    # event4 = c.rollback(vnr, reason='test')
    # print(event4.event_log)
    # c.substrate_network.to_json('sn.json')

    # sn.to_json('sn.json')
    env = VNEEnvironment(c)
    env_checker.check_env(env)


if __name__ == '__main__':
    main()
