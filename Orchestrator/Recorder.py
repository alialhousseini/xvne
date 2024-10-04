''' Record Events in a file '''
from Networks import VirtualNetworkRequest
from utils import Event
# Arrival, Departure, Failure (capacity constraint/ non-complete allocation), Release, Allocation
# 1. Arrival: when a VNR arrives
# 2. Departure: when a VNR departs - requires a release
# 3. Failure: when a VNR fails - requires a rollback
# 4. Release: when a VNR is released - requires a rollback
# 5. Allocation: when a VNR is allocated - requires a rollback


class Recorder:
    def __init__(self, filename: str, log_level: str = 'AUTO') -> None:
        self.filename: str = filename
        self.arr_dep_events: list[Event] = []
        self.failure_events: list[FailureEvent] = []
        self.success_events: list[SuccessEvent] = []
        self.all_events: list = []
        
        self.all_events_count: int = 0
        self.arr_dep_events_count: int = 0
        self.failure_events_count: int = 0
        self.success_events_count: int = 0
        
        # By default: AUTO, the logging will be automatic
        self.log_level: str = log_level

    def add_arr_dep_event(self, event: Event) -> None:
        self.arr_dep_events.append(event)
        self.arr_dep_events_count += 1
        self.all_events_count += 1
        if self.log_level == 'AUTO':
            self.record_event(event)

    def record_event(self, event: Event) -> None:
        event.log_event(self.filename)

    def remove_event(self, event: Event) -> None:
        self.events.remove(event)

    def show_events(self) -> None:
        for event in self.events:
            print(event)
