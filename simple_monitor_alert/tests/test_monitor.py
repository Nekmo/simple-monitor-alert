import os
import unittest

from simple_monitor_alert.monitor import Monitor


DIR_PATH = os.path.dirname(os.path.abspath(__file__))

class TestMonitor(unittest.TestCase):

  def test_ok_execute(self):
      monitor = Monitor(os.path.join(DIR_PATH, 'assets', 'ok-monitor.py'))
      monitor.execute()


if __name__ == '__main__':
    unittest.main()