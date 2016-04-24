import subprocess
import string
import re
import sys
import warnings

from simple_monitor_alert.exceptions import InvalidScriptLineError, InvalidScriptLineWarning

TIMEOUT = 5
ENCODING = sys.getdefaultencoding()


class Line(object):
    pattern = None

    def __init__(self, line, monitor):
        self.line, self.monitor = line, monitor
        match = self.pattern.match(self.line)
        if match is None:
            raise InvalidScriptLineError(line, monitor.script_path)
        for key, value in match.groupdict().items():
            setattr(self, key, value)

    @staticmethod
    def parse(line, monitor):
        if isinstance(line, bytes):
            line = line.decode(ENCODING)
        line = line.strip(string.whitespace)
        if not line or line.startswith('#'):
            return
        for line_type_class in [ItemLine]:
            try:
                return line_type_class(line, monitor)
            except InvalidScriptLineError:
                pass
        raise InvalidScriptLineError(line, monitor.script_path)


class ItemLine(Line):
    key = ''
    value = ''
    pattern = re.compile('(?P<key>[A-z.()]+) ?\= ?(?P<value>.*)')


class Header(Line):
    key = ''
    value = ''
    pattern = re.compile('(?P<key>[A-z]+) ?\: ?(?P<value>.*)')


class Monitor(object):
    def __init__(self, script_path, config_path=None):
        self.script_path, self.config_path = script_path, config_path

    def execute(self):
        popen = subprocess.Popen([self.script_path], stdout=subprocess.PIPE)
        popen.wait(TIMEOUT)
        lines = self.parse_lines(popen.stdout.readlines())
        print(list(lines))

    def parse_lines(self, lines, on_error=InvalidScriptLineWarning):
        for i, line in enumerate(lines):
            try:
                yield Line.parse(line, self)
            except InvalidScriptLineError:
                if issubclass(on_error, Warning):
                    warnings.warn_explicit(on_error(line, self.script_path), on_error, self.script_path, i + 1)
                elif issubclass(on_error, Exception):
                    raise on_error(line, self.script_path)
