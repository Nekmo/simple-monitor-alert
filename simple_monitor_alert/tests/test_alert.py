import datetime
import os
import unittest

import dateutil

from simple_monitor_alert.alerts import Alerts
from simple_monitor_alert.lines import Observable, ItemLine
from simple_monitor_alert.tests.base import FakeSMA, FakeAlert, FakeConfig, TestBase

DIR_PATH = os.path.dirname(os.path.abspath(__file__))


class TestAlert(TestBase, unittest.TestCase):

    def setUp(self):
        pass

    def test_send(self):
        section = 'test-alert'
        sma = self.get_sma(section)
        alerts = self.get_alerts(section, sma)
        observable = self.get_observable()
        alerts.send_alerts(observable)
        self.assertIn(section, sma.results['monitors'][None]['test']['alerted'])
        self.assertEqual(alerts[0].executions, 1)
        # Prevent double execution
        alerts.send_alerts(observable)
        self.assertEqual(alerts[0].executions, 1)

    def test_graphic_peak(self):
        section = 'test-alert'
        sma = self.get_sma(section)
        alerts = self.get_alerts(section, sma)
        observable = self.get_observable()
        observable.add_line(ItemLine('test.seconds', '10'))
        alerts.send_alerts(observable)
        self.assertEqual(alerts[0].executions, 0)
        # Prevent double execution
        dt = datetime.datetime.now(dateutil.tz.tzlocal()) - datetime.timedelta(seconds=10)
        sma.results.get_observable_result(observable)['since'] = dt.isoformat()
        alerts.send_alerts(observable)
        self.assertEqual(alerts[0].executions, 1)


if __name__ == '__main__':
    unittest.main()
