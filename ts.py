import utils


class TS:
    def __init__(self, name, ts):
        self.name = name
        self.ts = ts

    def is_stationary(self):
        return utils.is_stationary(self.ts)