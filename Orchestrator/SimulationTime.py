'''Simulation time management module'''


class SimTime:
    '''
    A class for simulating time
    '''
    current_time = 0

    @classmethod
    def set_time(cls, time: int) -> None:
        if time >= cls.current_time:
            cls.current_time = time

    @classmethod
    def get_time(cls) -> int:
        return cls.current_time

    @classmethod
    def add_time(cls, time: int) -> None:
        cls.current_time += time

    @classmethod
    def reset_time(cls) -> None:
        cls.current_time = 0

    @classmethod
    def tick(cls) -> None:
        cls.current_time += 1
