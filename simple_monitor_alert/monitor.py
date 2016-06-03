import datetime
import os
import subprocess
import warnings
import logging
from collections import defaultdict
from time import sleep, time
from threading import Timer

import dateutil
import six
import sys

from dateutil.tz import tzlocal

from simple_monitor_alert.exceptions import InvalidScriptLineError, InvalidScriptLineLogging
from simple_monitor_alert.lines import Observable, RawLine, RawItemLine, get_observables_from_lines, RawHeaderLine

logger = logging.getLogger('sma')

TIMEOUT = 5


def get_verbose_condition(observable):
    value = observable.get_line_value('value')
    expected = observable.get_matcher()
    if hasattr(expected, 'pattern'):
        expected = expected.pattern
    elif expected:
        expected = expected.parse()
    if isinstance(expected, six.string_types) or isinstance(expected, int):
        expected = '== {}'.format(expected)
    return '{} {}'.format(value, expected)


def log_evaluate(observable, result=None, use_logger=True):
    from simple_monitor_alert.sma import get_hostname
    result = result or observable.evaluate()
    level = 'success' if result else observable.get_line_value('level') or 'warning'
    msg = '{} - - Trigger: [{}] ({}) {}. '.format(get_hostname(), level,
                                                  getattr(getattr(observable, 'monitor', None), 'name', '?'),
                                           observable.get_verbose_name_group())
    msg += ('Result: {}' if result else 'Assertion {} failed').format(get_verbose_condition(observable))
    if observable.param_used:
        msg += '. Param used: {}'.format(observable.param_used)
    extra_info = observable.get_line_value('extra_info')
    if extra_info:
        msg += '. Extra info: {}'.format(extra_info)
    if use_logger:
        getattr(logger, 'info' if result else 'warning')(msg)
    else:
        return msg


class Monitor(object):
    lines = None
    headers = None
    items = None
    timeout = None

    def __init__(self, script_path, sma=None):
        self.script_path = script_path
        self.sma = sma
        self.name = os.path.splitext(os.path.split(script_path)[1])[0]

    def _execute_process(self, env):
        lines = []
        popen = subprocess.Popen([self.script_path], stdout=subprocess.PIPE, env=env)

        l = self.get_timer(popen)
        started_at = time()
        # sleep(.1)

        # Realtime Read
        blocksize = 1
        line = b''
        missing_data = True
        while popen.poll() is None or missing_data:
            if self.timeout:
                # No need to wait for X-Timeout header
                blocksize = -1
            if popen.poll() is not None and missing_data:
                # I force the loop if is the last cycle
                blocksize = -1
                missing_data = False
            line += popen.stdout.read(blocksize)
            if b'\n' not in line:
                continue
            processed_lines = line.split(b'\n')
            for line in processed_lines:
                lines.append(line + b'\n')
                timeout = self.get_headers(self.parse_lines([line])).get('X-Timeout')
                timeout = int(timeout) if timeout is not None else None
                if timeout and self.timeout is None:
                    l.cancel()
                    l = self.get_timer(popen, timeout - (time() - started_at))
                self.timeout = timeout
        l.cancel()
        return lines

    def get_timer(self, popen, timeout=TIMEOUT):
        def terminate_popen():
            popen.terminate()
            popen.kill()
        timeout = timeout if timeout > 0 else 0
        l = Timer(timeout, terminate_popen)
        l.start()
        return l

    def execute(self, parameters=None):
        env = self.get_env(parameters)
        lines = self.parse_lines(self._execute_process(env))
        self.lines = list(lines)
        self.items = self.get_observables(self.lines, parameters)
        self.headers = self.get_headers(self.lines)
        # self.evaluate_items()
        return self.items.values()

    def get_env(self, parameters):
        env = os.environ
        if parameters:
            env = env.copy()
            env.update(parameters)
        return env

    def parse_lines(self, lines, on_error=InvalidScriptLineLogging):
        for i, line in enumerate(lines):
            try:
                yield RawLine.parse(line, self)
            except InvalidScriptLineError:
                if issubclass(on_error, Warning):
                    warnings.warn_explicit(on_error(line, self.script_path), on_error, self.script_path, i + 1)
                elif issubclass(on_error, Exception):
                    raise on_error(line, self.script_path)
                elif on_error is None:
                    pass
                else:
                    on_error(line, self.script_path)

    def save_headers(self):
        self.sma.monitors_info.set_headers(self, self.headers)
        self.sma.monitors_info.write()

    def get_header(self, header_key):
        return (self.sma.monitors_info.get_monitor(self, create=False) or {}).get('headers', {}).get(header_key)

    def save_last_execution(self):
        self.sma.monitors_info.set_last_execution(self)
        self.sma.monitors_info.write()

    def last_execution(self):
        data = self.sma.monitors_info.get_monitor(self, create=False) or {}
        last_execution = data.get('last_execution', None)
        if last_execution:
            return dateutil.parser.parse(last_execution).replace(tzinfo=tzlocal())

    def shoud_be_executed(self):
        last_execution = self.last_execution()
        run_every = self.get_header('X-Run-Every-Seconds')
        if not last_execution or not run_every:
            return True
        dt = datetime.datetime.now(dateutil.tz.tzlocal())
        return dt - last_execution >= datetime.timedelta(seconds=run_every)

    @staticmethod
    def get_observables(lines, params=None):
        return get_observables_from_lines(lines, params)

    @staticmethod
    def get_headers(lines):
        headers = {}
        for line in filter(lambda x: isinstance(x, RawHeaderLine), lines):
            headers[line.key] = line.value
        return headers


class Monitors(object):
    monitors = None
    _monitors_paths = None

    def __init__(self, monitors_dir=None, config=None, sma=None):
        self.monitors_dir, self.config = monitors_dir, config
        self.sma = sma

    def get_monitors(self, monitors_dir=None):
        if self.monitors:
            return self.monitors
        monitors_dir = monitors_dir or self.monitors_dir
        self.monitors = [self.get_monitor(x) for x in self._get_monitors_paths(monitors_dir)]
        return self.monitors

    def _get_monitors_paths(self, monitors_dir):
        if self._monitors_paths is None:
            self._monitors_paths =  [os.path.join(monitors_dir, file) for file in os.listdir(monitors_dir)]
        return self._monitors_paths

    def get_monitors_names(self, monitors_dir=None):
        monitors_dir = monitors_dir or self.monitors_dir
        return map(lambda x: os.path.splitext(x.split('/')[-1])[0], self._get_monitors_paths(monitors_dir))

    def is_monitor_enabled(self, name):
        return name in self.get_monitors_names()

    def get_monitor(self, script_path):
        return Monitor(script_path, self.sma)

    def get_monitor_params(self, monitor):
        observables = self.config.get_monitor_observables(monitor.name)
        if isinstance(observables, dict):
            observables = observables.values()
        return dict(filter(lambda x: x[1] is not None, [(observable.get_verbose_name_group(), observable.get_param())
                                                        for observable in observables]))

    @staticmethod
    def get_parameters_cycles(parameters):
        if not parameters:
            return [{}]
        names_parameters = defaultdict(list)
        for parameter, value in parameters.items():
            parameter = parameter.split('(')[0]
            names_parameters[parameter].append(value)
        cycles_num = len(sorted(names_parameters.items(), key=lambda x: len(x), reverse=True)[0])
        cycles = []
        for i in range(cycles_num):
            cycle = {}
            cycles.append(cycle)
            for key, values in names_parameters.items():
                cycle[key] = values[i % len(values)]
        return cycles

    def execute(self, monitor):
        parameters = self.get_monitor_params(monitor)
        observables = []
        try:
            for params in self.get_parameters_cycles(parameters):
                observables.extend(monitor.execute(params))
            monitor.save_headers()
            monitor.save_last_execution()
        except PermissionError:
            warnings.warn_explicit('No permissions for monitor. Check execution perms and read perms.',
                                   UserWarning, monitor.script_path, 1)
            return []
        new_observables = []
        for observable in observables:
            if observable not in new_observables:
                new_observables.append(observable)
        return new_observables

    def execute_all(self, use_config=True):
        for monitor in self.get_monitors():
            if not monitor.shoud_be_executed():
                continue
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
