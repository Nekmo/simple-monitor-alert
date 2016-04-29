import os
import subprocess
import warnings
import logging

import six

from simple_monitor_alert.exceptions import InvalidScriptLineError, InvalidScriptLineLogging
from simple_monitor_alert.lines import Observable, RawLine, RawItemLine, get_observables_from_lines

logger = logging.getLogger('sma')

TIMEOUT = 5


def get_verbose_condition(observable):
    value = observable.get_line_value('value')
    expected = observable.get_matcher()
    if expected:
        expected = expected.parse()
    if isinstance(expected, six.string_types):
        expected = '== {}'.format(expected)
    return '{} {}'.format(value, expected)


def log_evaluate(observable, result=None):
    result = result or observable.evaluate()
    level = 'success' if result else observable.get_line_value('level') or 'warning'
    msg = 'Trigger: [{}] {}. Result: {}'.format(level, observable.get_verbose_name(), get_verbose_condition(observable))
    extra_info = observable.get_line_value('extra_info')
    if extra_info:
        msg += '. Extra info: {}'.format(extra_info)
    getattr(logger, 'info' if result else 'warning')(msg)


class Monitor(object):
    lines = None
    headers = None
    items = None

    def __init__(self, script_path):
        self.script_path = script_path
        self.name = os.path.splitext(os.path.split(script_path)[1])[0]

    def execute(self, parameters=None):
        env = os.environ
        if parameters:
            env = env.copy()
            env = env.update(parameters)
        popen = subprocess.Popen([self.script_path], stdout=subprocess.PIPE, env=env)
        popen.wait(TIMEOUT)
        lines = self.parse_lines(popen.stdout.readlines())
        self.lines = list(lines)
        self.items = self.get_observables(self.lines)
        self.headers = self.get_headers(self.lines)
        # self.evaluate_items()
        return self.items.values()

    def evaluate_items(self, items_list=None):
        items = items_list or self.items.values()
        for item in items:
            log_evaluate(item)

    def parse_lines(self, lines, on_error=InvalidScriptLineLogging):
        for i, line in enumerate(lines):
            try:
                yield RawLine.parse(line, self)
            except InvalidScriptLineError:
                if issubclass(on_error, Warning):
                    warnings.warn_explicit(on_error(line, self.script_path), on_error, self.script_path, i + 1)
                elif issubclass(on_error, Exception):
                    raise on_error(line, self.script_path)
                else:
                    on_error(line, self.script_path)

    @staticmethod
    def get_observables(lines):
        return get_observables_from_lines(lines)

    @staticmethod
    def get_headers(lines):
        headers = {}
        for line in filter(lambda x: isinstance(x, RawItemLine), lines):
            headers[line.key] = line.value
        return headers


class Monitors(object):
    monitors = None

    def __init__(self, monitors_dir=None, config=None):
        self.monitors_dir, self.config = monitors_dir, config

    def get_monitors(self, monitors_dir=None):
        if self.monitors:
            return self.monitors
        monitors_dir = monitors_dir or self.monitors_dir
        self.monitors = [self.get_monitor(os.path.join(monitors_dir, file))
                         for file in os.listdir(monitors_dir)]
        return self.monitors

    @staticmethod
    def get_monitor(script_path):
        return Monitor(script_path)

    def get_monitor_params(self, monitor):
        observables = self.config.get_monitor_observables(monitor.name)
        if isinstance(observables, dict):
            observables = observables.values()
        return list(filter(lambda x: x is not None, [observable.get_param() for observable in observables]))

    def execute(self, monitor):
        parameters = self.get_monitor_params(monitor)
        try:
            observables = monitor.execute(parameters)
        except PermissionError:
            warnings.warn_explicit('No permissions for monitor. Check execution perms and read perms.',
                                   UserWarning, monitor.script_path, 1)
            return []
        return observables

    def execute_all(self, use_config=True):
        for monitor in self.get_monitors():
            observables = self.execute(monitor)
            if use_config:
                self.update_observables(monitor, observables)
            for observable in observables:
                observable.set_monitor(monitor)
                yield observable

    def update_observables(self, monitor, observables):
        for observable in observables:
            config_observable = self.config.get_observable(monitor.name, observable.name, observable.group)
            observable.update_usign_observable(config_observable)
