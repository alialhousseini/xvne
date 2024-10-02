''' Record Events in a file '''
from Network import VirtualNetworkRequest, SubstrateNetwork, SubstrateNode, SubstrateLink, VirtualNode, VirtualLink

# Arrival, Departure, Failure (capacity constraint/ non-complete allocation), Release, Allocation
# 1. Arrival: when a VNR arrives
# 2. Departure: when a VNR departs - requires a release
# 3. Failure: when a VNR fails - requires a rollback
# 4. Release: when a VNR is released - requires a rollback
# 5. Allocation: when a VNR is allocated - requires a rollback


class Event:
    def __init__(self, type: str, time: int, **kwargs):
        ''' Generate a list of possible kwargs for the event 
        Args:
            type: the type of event
            time: the time of the event
            **kwargs: the arguments of the event

        Kwargs:
            virtual_network_request: the virtual network request
            substrate_node: the substrate node
            substrate_link: the substrate link
            virtual_node: the virtual node
            virtual_link: the virtual link
        '''
        self.type: str = type
        self.time: int = time

        if type == 'Arr':
            # the arrival VNR
            self.virtual_network_request: VirtualNetworkRequest = kwargs[
                'virtual_network_request']
            self.event_detail = {'vnr_id': self.virtual_network_request.id,
                                 'arrival_time': self.virtual_network_request.arrival_time}

        elif type == 'Dep':
            # the departure VNR
            self.virtual_network_request = kwargs['virtual_network_request']
            self.actual_departure_time = kwargs['actual_departure_time']
            self.event_detail = {'vnr_id': self.virtual_network_request.id,
                                 'expected_departure_time': self.virtual_network_request.arrival_time + self.virtual_network_request.lifetime,
                                 'actual_departure_time': self.actual_departure_time}
            # This event requires a release, a controller will handle the release

        elif type == 'Fail':
            # A fail could be due to a capacity constraint
            # Or a non-complete allocation (e.g. a link is not possible to be allocated)
            self.virtual_network_request = kwargs['virtual_network_request']
            # the sub_type of the failure: 'Cap' or 'Link'
            self.sub_type = kwargs['sub_type']
            if self.sub_type == 'cap':
                self.sn = kwargs['sn']
                self.event_detail = {'vnr_id': self.virtual_network_request.id,
                                     'failure_type': 'cap',
                                     'sn': self.sn.id}
            elif self.sub_type == 'link':
                self.event_detail = {'vnr_id': self.virtual_network_request.id,
                                     'failure_type': 'Link'}
            else:
                raise ValueError('sub_type must be "cap" or "link"')

        # A release event could be added if it requires a considerable amount of time

        elif type == 'node_embedding':
            self.vn = kwargs['vn']
            self.sn = kwargs['sn']
            self.event_detail = {'vn_id': self.vn.id,
                                 'sn_id': self.sn.id}

        elif type == 'link_embedding':
            self.vl = kwargs['vl']
            self.vp = kwargs['vp']  # the substrate path
            self.event_detail = {'vl_id': self.vl.id,
                                 'vp': self.vp}

    def log_event(self, filename: str) -> None:
        with open(filename, 'a') as file:
            file.write(str(self) + '\n')


class Recorder:
    def __init__(self, filename: str):
        self.filename = filename
        self.events: list[Event] = []
        self.event_count = 0

    def add_event(self, event: Event) -> None:
        self.events.append(event)
        self.event_count += 1

    def record_event(self, event: Event) -> None:
        event.log_event(self.filename)
