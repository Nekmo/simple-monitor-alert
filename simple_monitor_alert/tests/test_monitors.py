import os
import unittest

from simple_monitor_alert.monitor import Monitors, Monitor
from simple_monitor_alert.tests.base import TestBase

DIR_PATH = os.path.dirname(os.path.abspath(__file__))


class TestMonitors(unittest.TestCase, TestBase):
    def get_monitors(self):
        sma = self.get_sma()
        return Monitors(os.path.join(DIR_PATH, 'assets', 'monitors'), sma=sma)

    def test_get_monitors(self):
        monitors = self.get_monitors()
        monitors_list = monitors.get_monitors()
        self.assertNotIn(False, map(lambda x: isinstance(x, Monitor), monitors_list))
        self.assertEqual(set(map(lambda x: x.script_path, monitors_list)),
                         set(map(lambda x: os.path.join(monitors.monitors_dir, x), os.listdir(monitors.monitors_dir))))

    def test_get_monitors_names(self):
        monitors = self.get_monitors()
        monitors_names = monitors.get_monitors_names()
        self.assertEqual(set(monitors_names),
                         set(map(lambda x: os.path.splitext(x.split('/')[-1])[0], os.listdir(monitors.monitors_dir))))

    def test_monitors_execute_all(self):
        monitors = self.get_monitors()
        list(monitors.execute_all())

    def test_parameters_cycles(self):
        monitors = self.get_monitors()

        def get_values_list(ls):
            return sorted(map(lambda x: sorted(list(x.items())), ls))

        def cycles_target(cycles, target):
            cycles = monitors.get_parameters_cycles(cycles)
            self.assertEqual(get_values_list(cycles), get_values_list(target))
        cycles_target({'foo': '3'}, [{'foo': '3'}])
        cycles_target({'foo(g1)': '1', 'foo(g2)': '2'}, [{'foo': '1'}, {'foo': '2'}])
        cycles_target({'foo(g1)': '1', 'foo(g2)': '2', 'bar': 'eggs'},
                      [{'foo': '1', 'bar': 'eggs'}, {'foo': '2', 'bar': 'eggs'}])

if __name__ == '__main__':
    unittest.main()
