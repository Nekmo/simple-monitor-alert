import six

from simple_monitor_alert.alerts import Alerts
from simple_monitor_alert.lines import ItemLine, Observable, get_observables_from_lines
from simple_monitor_alert.monitor import Monitors, log_evaluate

if six.PY2:
    from ConfigParser import ConfigParser
else:
    from configparser import  ConfigParser, NoSectionError


class Config(ConfigParser):
    def __init__(self, file):
        self.file = file
        super(Config, self).__init__()
        self.read(self.file)

    def get_monitor_observables(self, name):
        try:
            lines = self.items(name)
        except NoSectionError:
            return []
        lines = [ItemLine(key, value) for key, value in lines]
        return get_observables_from_lines(lines)

    def get_observable(self, monitor_name, observable_name, group_name=None):
        monitor = self.get_monitor_observables(monitor_name)
        if not monitor:
            return
        return monitor.get((observable_name, group_name), None)


class SMA(object):
    def __init__(self, monitors_dir=None, alerts_dir=None, config_file=None):
        self.config = Config(config_file)
        self.monitors = Monitors(monitors_dir, self.config)
        self.alerts = Alerts(self.config, alerts_dir)

    def evaluate_and_alert(self):
        observables = self.evaluate_all()
        fail_observables = [observable for (observable, result) in observables if not result]
        self.alert_all(fail_observables)

    def alert_all(self, observables, fail=True):
        for observable in observables:
            self.alerts.send_observable_result(observable, fail)

    def execute_all(self):
        return self.monitors.execute_all()

    def evaluate_all(self):
        observables = self.execute_all()
        for observable in observables:
            result = observable.evaluate()
            log_evaluate(observable, result)
            yield observable, result
