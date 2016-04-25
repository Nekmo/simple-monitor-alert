import os


class AlertBase(object):
    def __init__(self):
        self.config = os.environ
        self.init()

    def init(self):
        pass


class AlertsBase(object):
    pass
