import six

from simple_monitor_alert.monitor import Monitors

if six.PY2:
    from ConfigParser import ConfigParser
else:
    from configparser import  ConfigParser


class Config(ConfigParser):
    def __init__(self, file):
        self.file = file
        super(Config, self).__init__()
        self.read(self.file)


class SMA(object):
    def __init__(self, monitors_dir=None, config_file=None):
        self.config = Config(config_file)
        self.monitors = Monitors(monitors_dir, self.config)

    def execute_all(self):
        self.monitors.execute_all()
