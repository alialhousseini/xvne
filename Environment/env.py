'''OpenAI-Gym Environment for RL-VNE using SB3'''
import gymnasium as gym
import numpy as np
from gymnasium import spaces
from Orchestrator import Controller, SimTime
from utils import FailureEvent, SuccessEvent, ReleaseEvent

# Hopefully: This is all what you need


class VNEEnvironment(gym.Env):

    metadata = {"render_modes": ["human"], "render_fps": 30}

    def __init__(self, controller: Controller):
        super(VNEEnvironment, self).__init__()

        # Controller - main component
        self.controller = controller
        self.controller_copy = controller

        # Define action and observation space
        self.N_SUBSTRATE_NODES = len(
            self.controller.substrate_network.substrate_nodes)
        self.MAX_VNR_NODES = self.controller.get_max_num_nodes()
        self.N_VNRS = len(self.controller.vnrs)

        # action space is equal to the number of substrate nodes
        self.action_space = spaces.Discrete(self.N_SUBSTRATE_NODES)

        # observation space:
        # Is a dict:
        #   key1='substrate_network': value1='A matrix of shape (N_SUBSTRATE_NODES,3) where each row is a substrate node with 3 features: available_cap, node_degree, sum_of_bandwidths
        #   key2='current_vnr': value2= Dict:
        #        key2.1 = 'current_vnr_nodes': value2.1 = 'A matrix of shape (MAX_VNR_NODES,3) where each row is a virtual node with 3 features: available_cap, node_degree, sum_of_bandwidths
        #        key2.2 = 'vnr_mask': value2.2 = 'A vector of length MAX_VNR_NODES with 1 if the line represent a node in the current VNR and 0 otherwise' (aka MASKING)
        #   key3 = 'vnr_queue': value3 = Dict:
        #        key3.1 = 'queue_length': value3.1 = 'An integer representing the length of the queue, the number of VNRs not yet processed'
        #        key3.2 = 'next_event_type': value3.2 = 'An integer representing the type of the next event' (0: Arrival, 1: Departure)

        self.observation_space = spaces.Dict({
            'substrate_network': spaces.Box(
                low=0,
                high=np.inf,
                shape=(self.N_SUBSTRATE_NODES, 3),
                dtype=np.int32
            ),

            'current_vnr': spaces.Dict({

                'current_vnr_nodes': spaces.Box(
                    low=0,
                    high=np.inf,
                    shape=(self.MAX_VNR_NODES, 3),
                    dtype=np.int32
                ),

                'vnr_mask': spaces.MultiBinary(self.MAX_VNR_NODES),

            }),

            'vnr_queue': spaces.Dict({
                'queue_length': spaces.Discrete(self.N_VNRS),
                'next_event_type': spaces.Discrete(2)
            })

        })

    def reward_shape(self, event: SuccessEvent | FailureEvent, **kwargs) -> float:
        fully_emb = kwargs.get('fully_emb', False)
        reward = 0
        alpha = 0.7
        vnr = event.vnr
        vnode = event.vnode

        gamma_r = vnr.virtual_network.get_sum_vnode_resources(
            vnode) / vnr.get_sum_all_resources()

        if isinstance(event, SuccessEvent):

            try:
                gamma_a = 1/(len(vnr.vnodes_id) -
                             len(vnr.nodes_embedded_components.keys()))
            except ZeroDivisionError:
                gamma_a = 1

            reward += 100 * ((alpha * gamma_a) +
                             ((1 - alpha) * gamma_r))

        else:

            try:
                gamma_a = len(vnr.vnodes_id)/(len(vnr.vnodes_id) -
                                              len(vnr.nodes_embedded_components.keys()))
            except ZeroDivisionError:
                gamma_a = 1

            reward -= 100 * ((alpha * gamma_a) +
                             ((1 - alpha) * gamma_r))

        if fully_emb:
            reward += 100 * (1/self.N_VNRS)

        return reward

    def step(self, action):

        # action:
        snode_id: int = action

        # used to remark whether the episode is over
        done = False

        # initialize reward
        reward = 0

        # Retrieve the current event
        event = self.controller.recorder.arr_dep_events[0]
        # Retrieve the corresponding VNR from event
        current_vnr = event.vnr

        # Set time to the event's time: Don't worry for next iterations, the function will not change the time to the past
        SimTime.set_time(event.time)

        # Iterate through departure events and release VNRs
        while event.type == 'Dep':

            # Additional Check
            if len(self.controller.evaluator.processed_vnrs) == 0:
                raise ValueError(
                    'Logical Error: A departure event was found but with no VNR processed.'
                )

            # Release the VNR
            release_event = self.controller.rollback(current_vnr, 'Departed.')

            if release_event is None:
                raise ValueError(
                    'Logical Error: Something crazy happened.')

            # Record result
            self.controller.recorder.add_event(release_event)

            # We remove the current departure event
            self.controller.recorder.remove_event(event)

            # We check here if there are no more events
            if len(self.controller.recorder.arr_dep_events) == 0:
                # No longer events: The episode is over
                done = True
                break

            # We get next event
            event = self.controller.recorder.arr_dep_events[0]

        if event.type == 'Arr':

            # Allocate the node using the given action
            allocation_result = self.controller.allocate_vnode(
                current_vnr, snode_id)

            if allocation_result is None:
                raise ValueError(
                    'Logical Error: Something crazy happened.')

            # Record result
            self.controller.recorder.add_event(allocation_result)

            if isinstance(allocation_result, FailureEvent):
                # Failure: This VNR cannot be embedded, we skip it
                # We rollback the current VNR
                release_event = self.controller.rollback(
                    current_vnr, 'Embedding is failed.')

                # Record rollback event
                self.controller.recorder.add_event(release_event)

                # We skip current VNR
                self.controller.evaluator.processed_vnrs += 1

                # We remove the current arrival event
                self.controller.recorder.remove_event(event)

                # Negative Reward
                reward = self.reward_shape(allocation_result)

            else:  # IsInstance of SuccessEvent

                # Positive Reward
                reward = self.reward_shape(event)

                # We check if the VNR is fully embedded
                if current_vnr.is_all_embedded():
                    # We remove the current arrival event
                    self.controller.recorder.remove_event(event)

                    # This VNR is fully embedded
                    # We mark it as processed
                    self.controller.evaluator.processed_vnrs += 1

                    # We give the agent a bonus for embedding the whole VNR
                    reward += self.reward_shape(event, fully_emb=True)

            # Outside if-else block
            if self.controller.evaluator.is_all_vnrs_processed():
                # All VNRs are processed
                if self.controller.evaluator.is_all_vnrs_embedded():
                    # It deserves a end-of-episode reward - if all VNR have been embedded
                    reward += 100

        # Observation formulation
        observation = self.extraction_representation()

        # End of experiment return
        return observation, reward, done, False, {}

    def extraction_representation(self):
        state_space = {}
        try:
            event = self.controller.recorder.arr_dep_events[0]
        except IndexError:
            return state_space

        sn_rep = np.zeros((self.N_SUBSTRATE_NODES, 3), dtype=np.int32)
        for i in range(self.N_SUBSTRATE_NODES):
            snode = self.controller.substrate_network.substrate_nodes[i]
            sn_rep[i, 0] = snode.available_capacity
            sn_rep[i, 1] = self.controller.substrate_network.get_node_degree(
                snode)
            sn_rep[i, 2] = self.controller.substrate_network.get_sum_bws_snode(
                snode)
        state_space['substrate_network'] = sn_rep

        vnr = event.vnr

        vnr_dict = {}
        vnr_rep = -1*np.zeros((self.MAX_VNR_NODES, 3), dtype=np.int32)
        for i in range(self.MAX_VNR_NODES):
            vnode = vnr.virtual_network.virtual_nodes[i]
            vnr_rep[i, 0] = vnode.available_capacity
            vnr_rep[i, 1] = vnr.virtual_network.get_node_degree(vnode)
            vnr_rep[i, 2] = vnr.virtual_network.get_sum_bws_vnodes(vnode)
        vnr_dict['current_vnr_nodes'] = vnr_rep
        # rows that starts with -1
        vnr_dict['vnr_mask'] = (vnr_rep[0, :] != -1).astype(np.int32)

        state_space['current_vnr'] = vnr_dict

        vnr_queue = {}
        vnr_queue['queue_length'] = self.N_VNRS - \
            self.controller.evaluator.processed_vnrs - 1

        vnr_queue['next_event_type'] = 0 if event.type == 'Arr' else 1

        state_space['vnr_queue'] = vnr_queue

        return state_space

    def generate_controller_copy(self):
        return self.controller_copy

    def generate_random_controller(self):
        pass

    def reset(self, seed=None, options=None):
        self.controller = self.generate_controller_copy()
        self.N_SUBSTRATE_NODES = len(
            self.controller.substrate_network.substrate_nodes)
        self.MAX_VNR_NODES = self.controller.get_max_num_nodes()
        self.N_VNRS = len(self.controller.vnrs)
        observation, info = self.extraction_representation(), {}
        return observation, info

    def render(self):
        pass

    def close(self):
        pass
