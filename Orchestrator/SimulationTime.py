'''Simulation time management module'''


class SimTime:

    def __init__(self):
        self.time = 0

    def tick(self):
        self.time += 1

    def get_time(self):
        return self.time

    def reset(self):
        self.time = 0

    def add_time(self, time):
        self.time += time

    def set_time(self, time):
        if time >= self.time:
            self.time = time
