import os
import unittest

from simple_monitor_alert.monitor import Monitor, ItemLine
from simple_monitor_alert.lines import Item, ItemLine

DIR_PATH = os.path.dirname(os.path.abspath(__file__))

class TestItem(unittest.TestCase):

    def setUp(self):
        self.monitor = Monitor('/fake/script')

    def test_default_true(self):
        for value in ['true', 'True', 'yes', 'Yes', '0']:
            item = Item(self.monitor, 'test')
            item.add_line(ItemLine('test.value={}'.format(value), self))
            self.assertTrue(item.evaluate())

    def test_default_equal(self):
        item = Item(self.monitor, 'test')
        item.add_line(ItemLine('test.expected=foo', self))
        item.add_line(ItemLine('test.value=foo', self))
        self.assertTrue(item.evaluate())


if __name__ == '__main__':
    unittest.main()