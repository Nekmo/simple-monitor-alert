import os
import sys
from configparser import NoSectionError

from simple_monitor_alert.alerts import Alerts
from simple_monitor_alert.lines import Observable, ItemLine
from simple_monitor_alert.monitor import Monitors
from simple_monitor_alert.sma import Results, Config, MonitorsInfo
from simple_monitor_alert.utils.files import JSONFile

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MONITORS_DIR = os.path.join(BASE_DIR, 'assets', 'monitors')


class FakeJSONFile(JSONFile):
    def __init__(self, data):
        super(FakeJSONFile, self).__init__('/Fake-JSON-File', create=False)
        self.update(data)

    def read(self):
        pass

    def write(self):
        pass


class FakeObservableResults(FakeJSONFile, Results):
    monitor = None

    def __init__(self, data=None, sma=None):
        data = data or {'monitors': {}}
        super(FakeObservableResults, self).__init__(data)
        self.sma = sma

    def get_observable_result(self, observable):
        monitor = self['monitors'].get(getattr(observable, 'monitor', self.monitor), {})
        result = monitor.get(observable.name, self.get_default_observable_result())
        monitor[observable.name] = result
        self['monitors'][getattr(observable, 'monitor', self.monitor)] = monitor
        return result


class FakeMonitorsInfo(FakeJSONFile, MonitorsInfo):
    pass


class FakeMonitors(Monitors):
    pass


class FakeSMA(object):
    def __init__(self, config=None, monitors_info=None, monitors_dir=MONITORS_DIR):
        self.results = FakeObservableResults()
        self.monitors_info = monitors_info or FakeMonitorsInfo({})
        self.config = config
        self.monitors = FakeMonitors(monitors_dir, sma=self)


class FakeAlert(object):
    executions = 0

    def __init__(self, section):
        self.section = section

    def send(self, *args, **kwargs):
        self.executions += 1
        return True


class FakeConfig(Config):
    def __init__(self, data):
        if sys.version_info >= (3, 0):
            super().__init__('/Fake-Config-File')
        else:
            # Old Style Class
            Config.__init__(self, '/Fake-Config-File')
        self._data = data

    def items(self, section=None, **kwargs):
        try:
            return self._data[section]
        except KeyError:
            raise NoSectionError(section)


class TestBase(object):
    def get_observable(self):
        observable = Observable('test')
        observable.add_line(ItemLine('test.expected', '20'))
        observable.add_line(ItemLine('test.value', '19'))
        return observable

    def get_alerts(self, section, sma):
        alerts_modules = [FakeAlert(section)]
        alerts = Alerts(sma, '/Fake-Alerts-Dir', alerts_modules, [section])
        return alerts

    def get_results(self, data=None, monitors_info=None):
        return FakeObservableResults(data, FakeSMA(monitors_info=monitors_info).monitors_info)

    def get_sma(self, section=None, monitors_info=None):
        config = FakeConfig({section: ()})
        sma = FakeSMA(config, monitors_info=monitors_info)
        return sma