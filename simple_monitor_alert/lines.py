import re
import string
import sys

import six

from simple_monitor_alert.exceptions import InvalidScriptLineError


ENCODING = sys.getdefaultencoding()


class Operator(object):
    operator = None

    def __init__(self, value):
        self.value = value

    def match(self, other):
        raise NotImplementedError

    @staticmethod
    def get_operator(operator_symbol):
        try:
            return {'<': LeOperator, '<=': LeOperator, '==': EqOperator, '!=': NeOperator, '>=': GeOperator,
                    '>': GeOperator}[operator_symbol]
        except:
            raise ValueError('Invalid operator: {}'.format(operator_symbol))

    @classmethod
    def get_class(cls, operator_symbol, value):
        return cls.get_operator(operator_symbol)(value)

    def __str__(self):
        return '{} {}'.format(self.operator, self.value)

    def __repr__(self):
        return self.__repr__()

class LtOperator(Operator):
    operator = '<'

    def match(self, other):
        return other < self.value


class LeOperator(Operator):
    operator = '<='

    def match(self, other):
        return other <= self.value


class EqOperator(Operator):
    operator = '=='

    def match(self, other):
        return other == self.value


class NeOperator(Operator):
    operator = '!='

    def match(self, other):
        return other != self.value


class GeOperator(Operator):
    operator = '>='

    def match(self, other):
        return other >= self.value


class GtOperator(Operator):
    operator = '>'

    def match(self, other):
        return other > self.value


def regex_match_parser(value):
    if not value.startswith('/'):
        raise ValueError('Invalid regex function: It must start with slash.')
    used_flags = value.split('/')[-1]
    flags = []
    for flag in used_flags:
        flag = getattr(re, flag.upper(), None)
        if not flag:
            raise ValueError('Invalid flag in regex function: {}.'.format(flag))
        flags.append(flag)
    return re.compile(value, flags)


class MatchParser(object):
    delimiters = ['"', "'"]

    def __init__(self, matcher):
        self.functions = {'r': regex_match_parser}
        self.matcher = matcher

    def parse_delimiter(self, matcher):
        for delimiter in self.delimiters:
            # Match "text", 'text', f'text' ...
            pos = matcher.find(delimiter)
            if pos == -1 or matcher[-1] != delimiter:
                continue
            if pos != 0:
                # Is function
                function = matcher[:pos]
                matcher = matcher[pos + len(function) + len(delimiter):]
                return self.functions[function](matcher)
            else:
                # Is string
                return matcher[len(delimiter):]

    @staticmethod
    def parse_common_types(match):
        if match.isdigit():
            # Is int
            return int(match)
        try:
            # Is float
            return float(match)
        except ValueError:
            pass

    def parse_operators(self, value):
        value = value.lstrip(string.whitespace)
        operator = value[0:2]
        try:
            operator_class = Operator.get_operator(operator)
        except ValueError:
            return
        value = value.replace(operator, '', 1).strip(string.whitespace)
        value = self.parse_value(value)
        return operator_class(value)

    def parse(self, match=None, matchers=None):
        matchers = matchers or [self.parse_delimiter, self.parse_operators, self.parse_common_types]
        if match is None:
            match = self.matcher
        for matcher in matchers:
            parser_value = matcher(match)
            if parser_value is not None:
                return parser_value
        return match

    def parse_value(self, value):
        return self.parse(value, [self.parse_common_types])

    def match(self, value):
        matcher = self.parse()
        value = self.parse_value(value)
        try:
            return matcher.match(value)
        except AttributeError:
            return matcher == value

    def __repr__(self):
        return '<MatcherParser \'{}\' ({})>'.format(self.matcher, self.parse())


class DefaultMatcher(object):
    value = re.compile('yes|true|0', re.IGNORECASE)


class Item(dict):
    group_pattern = re.compile('(?P<name>[A-z]+)\((?P<group>[A-z]+)\) *')

    def __init__(self, monitor, name, group=None):
        super(Item, self).__init__()
        from simple_monitor_alert.monitor import Monitor
        assert isinstance(monitor, Monitor)
        self.monitor = monitor
        self.name = name
        self.group = group

    def add_line(self, line):
        self[self.get_parameter(line.key)] = line

    @staticmethod
    def get_parameter(key):
        return key.split('.')[1]  # Ignore for now extra dotted parameters

    @classmethod
    def get_name_group(cls, key):
        name = key.split('.', 1)[0]
        group = cls.group_pattern.match(name)
        if group:
            name = group.groupdict()['name']
            group = group.groupdict()['group']
        return name, group

    def get_matcher(self):
        match = self.get('expected', DefaultMatcher).value
        if isinstance(match, six.string_types):
            return MatchParser(match)
        return match

    def get_item_value(self, item_name, default=None):
        try:
            return self[item_name].value
        except KeyError:
            return default

    def evaluate(self, value=None):
        if value is None:
            value = self['value'].value
        matcher = self.get_matcher()
        return matcher.match(value)

    def get_verbose_name(self):
        name = self.get('name')
        if name:
            return name.value
        else:
            return self.name


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
    pattern = re.compile('(?P<key>[A-z0-9.()_]+) ?= ?(?P<value>.*)')

    def __str__(self):
        return '{} = {}'.format(self.key, self.value)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.key == other.key and self.value == other.value


class Header(Line):
    key = ''
    value = ''
    pattern = re.compile('(?P<key>[A-z]+) ?: ?(?P<value>.*)')
