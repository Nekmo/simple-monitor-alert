import sys

from simple_monitor_alert.alerts import Alerts
from simple_monitor_alert.lines import Observable, ItemLine
from simple_monitor_alert.sma import JSONFile, ObservableResults, Config


class FakeJSONFile(JSONFile):
    def __init__(self, data):
        super(FakeJSONFile, self).__init__('/Fake-JSON-File', create=False)
        self.update(data)

    def read(self):
        pass

    def write(self):
        pass


class FakeObservableResults(FakeJSONFile, ObservableResults):
    monitor = None

    def __init__(self, data=None):
        data = data or {'monitors': {}}
        super(FakeObservableResults, self).__init__(data)

    def get_observable_result(self, observable):
        monitor = self['monitors'].get(getattr(observable, 'monitor', self.monitor), {})
        result = monitor.get(observable.name, self.get_default_observable_result())
        monitor[observable.name] = result
        self['monitors'][getattr(observable, 'monitor', self.monitor)] = monitor
        return result


class FakeSMA(object):
    def __init__(self, config=None):
        self.results = FakeObservableResults()
        self.config = config


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
        return self._data[section]


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

    def get_sma(self, section):
        config = FakeConfig({section: ()})
        sma = FakeSMA(config)
        return sma