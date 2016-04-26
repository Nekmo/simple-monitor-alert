import os
import unittest

from simple_monitor_alert.monitor import Monitor
from simple_monitor_alert.lines import Observable, RawItemLine

DIR_PATH = os.path.dirname(os.path.abspath(__file__))


class TestItem(unittest.TestCase):

    def setUp(self):
        self.monitor = Monitor('/fake/script')

    def test_default_true(self):
        for value in ['true', 'True', 'yes', 'Yes', '0']:
            item = Observable('test')
            item.add_line(RawItemLine('test.value={}'.format(value), self))
            self.assertTrue(item.evaluate())

    def test_default_equal(self):
        item = Observable('test')
        item.add_line(RawItemLine('test.expected=foo', self))
        item.add_line(RawItemLine('test.value=foo', self))
        self.assertTrue(item.evaluate())


if __name__ == '__main__':
    unittest.main()
