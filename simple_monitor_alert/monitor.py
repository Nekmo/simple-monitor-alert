import subprocess
import warnings

from simple_monitor_alert.exceptions import InvalidScriptLineError, InvalidScriptLineWarning
from simple_monitor_alert.lines import Item, Line, ItemLine

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

    def parse_lines(self, lines, on_error=InvalidScriptLineWarning):
        for i, line in enumerate(lines):
            try:
                yield Line.parse(line, self)
            except InvalidScriptLineError:
                if issubclass(on_error, Warning):
                    warnings.warn_explicit(on_error(line, self.script_path), on_error, self.script_path, i + 1)
                elif issubclass(on_error, Exception):
                    raise on_error(line, self.script_path)

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
