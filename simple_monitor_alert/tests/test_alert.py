import os
import unittest

from simple_monitor_alert.alerts import Alerts
from simple_monitor_alert.lines import Observable, ItemLine
from simple_monitor_alert.tests.base import FakeSMA, FakeAlert, FakeConfig

DIR_PATH = os.path.dirname(os.path.abspath(__file__))


class TestAlert(unittest.TestCase):

    def setUp(self):
        pass

    def test_send(self):
        section = 'test-alert'
        config = FakeConfig({section: ()})
        sma = FakeSMA(config)
        alerts_modules = [FakeAlert(section)]
        alerts = Alerts(sma, '/Fake-Alerts-Dir', alerts_modules, [section])
        observable = Observable('test')
        observable.add_line(ItemLine('test.expected', '20'))
        observable.add_line(ItemLine('test.value', '19'))
        alerts.send_alerts(observable)
        self.assertIn(section, sma.results['monitors'][None]['test']['alerted'])
        self.assertEqual(alerts_modules[0].executions, 1)
        # Prevent double execution
        alerts.send_alerts(observable)
        self.assertEqual(alerts_modules[0].executions, 1)

    def test_graphic_peak(self):
        pass


if __name__ == '__main__':
    unittest.main()
