''' Record Events in a file '''
from Networks import VirtualNetworkRequest
from utils import Arr_Dep_Event, FailureEvent, SuccessEvent, ReleaseEvent
# Arrival, Departure, Failure (capacity constraint/ non-complete allocation), Release, Allocation
# 1. Arrival: when a VNR arrives
# 2. Departure: when a VNR departs - requires a release
# 3. Failure: when a VNR fails - requires a rollback
# 4. Release: when a VNR is released - requires a rollback
# 5. Allocation: when a VNR is allocated - requires a rollback


class Recorder:
    def __init__(self, filename: str, log_level: str = 'AUTO') -> None:
        self.filename: str = filename
        self.arr_dep_events: list[Arr_Dep_Event] = []
        self.failure_events: list[FailureEvent] = []
        self.success_events: list[SuccessEvent] = []
        self.all_events: list = []

        self.all_events_count: int = 0
        self.arr_dep_events_count: int = 0
        self.failure_events_count: int = 0
        self.success_events_count: int = 0

        # By default: AUTO, the logging will be automatic
        self.log_level: str = log_level

    def add_event(self, event: SuccessEvent | FailureEvent | Arr_Dep_Event | ReleaseEvent) -> None:
        self.all_events.append(event)
        self.all_events_count += 1
        if event.type == 'Arr' or event.type == 'Dep':
            self.arr_dep_events_count += 1
            self.arr_dep_events.append(event)
        elif event.type == 'Node_Failure' or event.type == 'Link_Failure':
            self.failure_events_count += 1
            self.failure_events.append(event)
        elif event.type == 'Node_Success' or event.type == 'Link_Success':
            self.success_events_count += 1
            self.success_events.append(event)
        else:
            raise ValueError("The type of event is Unkown.")

        if self.log_level == 'AUTO':
            event.log_event(self.filename)

    def remove_event(self, event: Arr_Dep_Event) -> None:
        # this function is only for the Arr_Dep_Event, once a node is arrived we delete its record, same for departure
        self.arr_dep_events.remove(event)
        self.arr_dep_events_count -= 1

    def show_events(self) -> None:
        for event in self.all_events:
            print(event)
