import os
import unittest

from simple_monitor_alert.monitor import Monitor
from simple_monitor_alert.lines import Observable, RawItemLine

DIR_PATH = os.path.dirname(os.path.abspath(__file__))


def get_monitor_path(monitor):
    return os.path.join(DIR_PATH, 'assets', 'monitors', monitor)


class FakedError(Exception):
    pass


class TestMonitor(unittest.TestCase):

    def test_ok_execute(self):
        monitor = Monitor(get_monitor_path('ok-monitor.py'))
        monitor.execute()
        item = Observable('test')
        item.add_line(RawItemLine('test.expected=1', self))
        item.add_line(RawItemLine('test.value=1', self))
        self.assertIn((item.name, None), monitor.items.keys())
        self.assertEqual(item, monitor.items[(item.name, None)])

    def test_get_header(self):
        monitor = Monitor(get_monitor_path('run-every.py'))
        monitor.execute()

    def test_invalid_line(self):
        monitor = self.get_faked_monitor()
        line = 'Spam spam eggs'
        execution_data = []

        def execute(line, script_path):
            execution_data.extend([line, script_path])
        with self.assertRaises(FakedError):
            next(monitor.parse_lines([line], FakedError))
        with self.assertRaises(StopIteration):
            next(monitor.parse_lines([line], None))
        with self.assertRaises(StopIteration):
            next(monitor.parse_lines([line], execute))
        self.assertEqual(execution_data, [line, monitor.script_path])

    def get_faked_monitor(self):
        return Monitor('')


if __name__ == '__main__':
    unittest.main()
