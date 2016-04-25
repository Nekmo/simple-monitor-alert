import os
import subprocess
import warnings
import logging

import six

from simple_monitor_alert.exceptions import InvalidScriptLineError, InvalidScriptLineLogging
from simple_monitor_alert.lines import Item, Line, ItemLine

logger = logging.getLogger('sma')

TIMEOUT = 5


class Monitor(object):
    lines = None
    headers = None
    items = None

    def __init__(self, script_path, config_path=None):
        self.script_path, self.config_path = script_path, config_path

    def execute(self):
        popen = subprocess.Popen([self.script_path], stdout=subprocess.PIPE)
        popen.wait(TIMEOUT)
        lines = self.parse_lines(popen.stdout.readlines())
        self.lines = list(lines)
        self.items = self.get_items(self.lines)
        self.headers = self.get_headers(self.lines)
        self.evaluate_items()

    def evaluate_items(self, items_list=None):
        items = items_list or self.items.values()
        for item in items:
            self.print_evaluate(item)

    def print_evaluate(self, item):
        result = item.evaluate()
        level = 'success' if result else item.get_item_value('level') or 'warning'
        value = item.get_item_value('value')
        expected = item.get_matcher()
        if expected:
            expected = expected.parse()
        if isinstance(expected, six.string_types):
            expected = '== {}'.format(expected)
        msg = 'Trigger: [{}] {}. Result: {} {}'.format(level, item.get_verbose_name(), value, expected)
        extra_info = item.get_item_value('extra_info')
        if extra_info:
            msg += '. Extra info: {}'.format(extra_info)
        getattr(logger, 'info' if result else 'warning')(msg)

    def parse_lines(self, lines, on_error=InvalidScriptLineLogging):
        for i, line in enumerate(lines):
            try:
                yield Line.parse(line, self)
            except InvalidScriptLineError:
                if issubclass(on_error, Warning):
                    warnings.warn_explicit(on_error(line, self.script_path), on_error, self.script_path, i + 1)
                elif issubclass(on_error, Exception):
                    raise on_error(line, self.script_path)
                else:
                    on_error(line, self.script_path)

    def get_items(self, lines):
        items = {}
        lines_items = filter(lambda x: isinstance(x, ItemLine), lines)
        for line in lines_items:
            name, group = Item.get_name_group(line.key)
            if (name, group) not in items:
                items[name, group] = Item(self, name, group)
            items[name, group].add_line(line)
        return items

    @staticmethod
    def get_headers(lines):
        headers = {}
        for line in filter(lambda x: isinstance(x, ItemLine), lines):
            headers[line.key] = line.value
        return headers


class Monitors(object):
    monitors = None

    def __init__(self, monitors_dir=None, settings_file=None, settings_dir=None):
        self.monitors_dir, self.settings_file, self.settings_dir = monitors_dir, settings_file, settings_dir

    def get_monitors(self, monitors_dir=None, settings_dir=None):
        if self.monitors:
            return self.monitors
        monitors_dir = monitors_dir or self.monitors_dir
        settings_dir = settings_dir or self.settings_dir
        self.monitors = [self.get_monitor(os.path.join(monitors_dir, file), settings_dir)
                         for file in os.listdir(monitors_dir)]
        return self.monitors

    @staticmethod
    def get_monitor(script_path, settings_dir=None):
        config_path = os.path.join(settings_dir, os.path.splitext("script_path")[0] + '.ini')
        if not os.path.lexists(config_path):
            config_path = None
        return Monitor(script_path, config_path)

    def execute_all(self):
        for monitor in self.get_monitors():
            try:
                monitor.execute()
            except PermissionError:
                warnings.warn_explicit('No permissions for monitor. Check execution perms and read perms.',
                                       UserWarning, monitor.script_path, 1)
