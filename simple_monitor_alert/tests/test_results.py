import os
import unittest

from simple_monitor_alert.monitor import Monitors, Monitor
from simple_monitor_alert.tests.base import TestBase

DIR_PATH = os.path.dirname(os.path.abspath(__file__))


RESULTS_DATA = {
    'monitors': {
        "mdadm": {
            "mdadm(md0)": {
                "alerted": [],
                "executions": 9572,
                "fail": False,
                "since": "2016-05-25T15:37:07.865808+02:00",
                "updated_at": "2016-06-05T05:19:40.442957+02:00"
            }
        }
    }
}


class TestResults(unittest.TestCase, TestBase):
    def test_print_empty_results(self):
        self.assertEqual(str(self.get_results()), '')

    def test_print_results(self):
        str(self.get_results(RESULTS_DATA, self.get_sma()))

if __name__ == '__main__':
    unittest.main()
