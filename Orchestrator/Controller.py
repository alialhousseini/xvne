'''The GodFather of the scenario'''
from Networks import SubstrateNetwork
from utils import Event
from .Recorder import Recorder


class Controller:
    '''The GodFather of the scenario
        It controls all required components of the scenario.
        It manages the arrival/departure of VNRs
        It manages the failure of VNRs
    '''

    def __init__(self, substrate_network: SubstrateNetwork, vnrs: list) -> None:
        self.substrate_network = substrate_network
        self.vnrs = vnrs
        # A dict of VNRs, key = VNR id, value = VNR
        self.vnr_dict: dict = {vnr.id: vnr for vnr in vnrs}
        self.vnrs_embedded: int = 0
        # supposing current_time_at_beginning = 0
        # Initilize a recorder to record events
        # The recorder has a list of events to record all events
        self.recorder: Recorder = Recorder('Controller.txt')
        self.create_events()  # create arrival and departure events in an ordered list

    def create_events(self) -> None:
        for vnr in self.vnrs:
            self.recorder.add_event(Event('Arr', vnr.arrival_time, vnr))
        for vnr in self.vnrs:
            self.recorder.add_event(
                Event('Dep', vnr.arrival_time + vnr.lifetime, vnr))
        self.recorder.events.sort(key=lambda x: x.time)

    