'''OpenAI-Gym Environment for RL-VNE using SB3'''
import gymnasium as gym
import numpy as np
from gymnasium import spaces
from Orchestrator import Controller
from utils import FailureEvent, SuccessEvent, ReleaseEvent
# Hopefully: This is all what you need


class VNEEnvironment(gym.Env):

    metadata = {"render_modes": ["human"], "render_fps": 30}

    def __init__(self, controller: Controller):
        super(VNEEnvironment, self).__init__()

        # Controller - main component
        self.controller = controller

        # episode length
        self.episode_length = len(controller.vnrs)

        # current_vnr_index: int
        self.current_vnr_index = 0

        # Define action and observation space
        N_SUBSTRATE_NODES = len(
            self.controller.substrate_network.substrate_nodes)
        MAX_VNR_NODES = self.controller.get_max_num_nodes()
        N_VNRS = len(self.controller.vnrs)

        # action space is equal to the number of substrate nodes
        self.action_space = spaces.Discrete(N_SUBSTRATE_NODES)

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
                shape=(N_SUBSTRATE_NODES, 3),
                dtype=np.int32
            ),

            'current_vnr': spaces.Dict({

                'current_vnr_nodes': spaces.Box(
                    low=0,
                    high=np.inf,
                    shape=(MAX_VNR_NODES, 3),
                    dtype=np.int32
                ),

                'vnr_mask': spaces.MultiBinary(MAX_VNR_NODES),

            }),

            'vnr_queue': spaces.Dict({
                'queue_length': spaces.Discrete(N_VNRS),
                'next_event_type': spaces.Discrete(2)
            })

        })

    def step(self, action):

        # action:
        snode_id: int = action

        # Retrieve the current event
        event = self.controller.recorder.arr_dep_events[0]
        # Retrieve the corresponding VNR
        current_vnr = event.vnr

        # Set time to the event's time: Don't worry in next iterations, the function will not change the time to the past
        self.controller.time.set_time(event.time)

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

                # We remove the current arrival event
                self.controller.recorder.remove_event(event)

                # Negative Reward
                reward = -1

                return

            else:  # IsInstance of SuccessEvent

                # Positive Reward
                reward = 1

                if current_vnr.is_all_embedded():
                    # We remove the current arrival event
                    self.controller.recorder.remove_event(event)
                    # We give the agent a bonus for embedding the whole VNR
                    reward = 10

                return

        else:  # Event type is 'Dep'

            # Release the VNR
            release_event = self.controller.rollback(current_vnr, 'Departed.')

            if release_event is None:
                raise ValueError(
                    'Logical Error: Something crazy happened.')

            # Record result
            self.controller.recorder.add_event(release_event)

            return

    def reset(self, seed=None, options=None):
        ...
        return observation, info

    def render(self):
        ...

    def close(self):
        ...
