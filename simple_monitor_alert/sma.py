import datetime
import os
import sys
import time
import logging

import json
from operator import itemgetter
from collections import OrderedDict

import dateutil
import dateutil.parser
import dateutil.tz
import six
import socket

if six.PY3 and sys.version_info < (3,3):
    class _MetaColor(type):
        def __getattr__(self, item):
            return lambda x: x

    class Color(six.with_metaclass(_MetaColor)):
        pass
else:
    from colorclass import Color
from humanize.time import naturaltime
import terminaltables

if hasattr(terminaltables, '__version__') and terminaltables.__version__ >= '3.0.0':
    from terminaltables.other_tables import UnixTable
else:
    from terminaltables.tables import UnixTable

from simple_monitor_alert import __version__
from simple_monitor_alert.alerts import Alerts
from simple_monitor_alert.lines import ItemLine, Observable, get_observables_from_lines
from simple_monitor_alert.monitor import Monitors, log_evaluate
from simple_monitor_alert.utils.dates import human_since

if six.PY2:
    from ConfigParser import ConfigParser
else:
    from configparser import ConfigParser, NoSectionError

WAIT_SECONDS = 60
DEFAULT_VAR_DIRECTORY = os.environ.get('VAR_DIRECTORY', '/var/lib/simple-monitor-alert')
logger = logging.getLogger('sma')


def get_hostname():
    return socket.gethostname()


def validate_write_dir(directory, log=lambda x: x):
    if os.path.lexists(directory) and os.access(directory, os.W_OK):
        return True
    if os.path.lexists(directory) and not os.path.exists(directory):
        log('{} exists but the destination does not exist. Is a broken link?'.format(directory))
        return False
    try:
        os.makedirs(directory, exist_ok=True)
    except OSError:
        log('No write permissions to the directory {}.'.format(directory))
        return False
    return os.access(directory, os.W_OK)


def create_file(path, content=''):
    if not isinstance(content, six.string_types):
        content = json.dumps(content)
    if not os.path.exists(path):
        with open(path, 'w') as f:
            f.write(content)
    return path


def get_var_directory():
    var_directory = DEFAULT_VAR_DIRECTORY
    if validate_write_dir(var_directory, logger.warning):
        return var_directory
    for candidate in [os.path.expanduser('~/.local/var/lib/simple-monitor-alert'), '/tmp/simple-monitor-alert']:
        if validate_write_dir(candidate):
            logger.info('Usign {} directory for var content, but {} is recommended.'.format(candidate, var_directory))
            return candidate
    import getpass
    raise OSError('{} is not writable by {} user'.format(var_directory, getpass.getuser()))


class Config(ConfigParser):
    def __init__(self, file):
        self.file = file
        if sys.version_info >= (3, 0):
            super().__init__()
        else:
            # Old Style Class
            ConfigParser.__init__(self)
        self.read(self.file)

    def get_monitor_observables(self, name):
        try:
            lines = self.items(name)
        except NoSectionError:
            return []
        lines = [ItemLine(key, value) for key, value in lines]
        return get_observables_from_lines(lines)

    def get_observable(self, monitor_name, observable_name, group_name=None):
        monitor = self.get_monitor_observables(monitor_name)
        if not monitor:
            return
        return monitor.get((observable_name, group_name), None)


class JSONFile(dict):
    def __init__(self, path, create=True):
        super(JSONFile, self).__init__()
        if create:
            create_file(path, '{}')
        self.path = path
        self.read()

    def read(self):
        self.clear()
        self.update(json.load(open(self.path)))

    def write(self):
        json.dump(self, open(self.path, 'w'), sort_keys=True, indent=4, separators=(',', ': '))

    def clear(self):
        if sys.version_info >= (3, 3):
            super().clear()
        else:
            self[:] = []


class MonitorResults(object):
    columns = OrderedDict([
        ('Name', itemgetter('name')),
        ('Status', lambda x: Color.red('FAIL') if x['fail'] else Color.green('OK')),
        ('Since', lambda x: human_since(x['since'], True)),
        ('Updated', lambda x: human_since(x['updated_at'], True)),
        ('Times', lambda x: str(x['executions'])),
    ])

    def __init__(self, monitor_name, monitor_results, sma=None):
        self.monitor_name = monitor_name
        self.monitor_results = monitor_results
        self.sma = sma

    def get_section(self):
        return self.monitor_name

    def get_results_columns(self, columns=None):
        for name, result in self.monitor_results.items():
            result = dict(result)
            result['name'] = name
            yield [fn(result) for fn in self.columns.values()]

    def __str__(self):
        return '{}\n'.format(UnixTable(list(self.get_results_columns())).table)


class Results(JSONFile):

    def __init__(self, path, create=True, sma=None):
        super(Results, self).__init__(path, create)
        self.sma = sma

    @staticmethod
    def get_default_observable_result():
        return {
            'since': None, 'updated_at': None, 'fail': None, 'executions': 0, 'alerted': []
        }

    def update_observable_result(self, observable, fail, notified=False):
        result = self.get_observable_result(observable)
        result['updated_at'] = datetime.datetime.now(dateutil.tz.tzlocal()).isoformat()
        if fail != result['fail']:
            result['since'] = result['updated_at']
            result['alerted'] = []
        result['fail'] = fail
        result['executions'] += 1

    def get_observable_result(self, observable):
        monitor_name = observable.monitor.name
        if monitor_name not in self['monitors']:
            self['monitors'][monitor_name] = {}
        monitor = self['monitors'][monitor_name]
        result = monitor.get(observable.name, self.get_default_observable_result())
        monitor[observable.name] = result
        return result

    def add_alert_to_observable_result(self, observable, alert):
        result = self.get_observable_result(observable)
        if alert not in result['alerted']:
            result['alerted'].append(alert)
            return True
        return False

    def __str__(self):
        table_data = [list(MonitorResults.columns.keys())]
        table_splitted = []
        sections = {}
        start_size = 4
        for name, monitor_results in self['monitors'].items():
            table_data.extend(MonitorResults(name, monitor_results, self.sma).get_results_columns())
            sections[len(table_data)-1] = name
        table = UnixTable(table_data)
        table = table.table.splitlines()
        head = '\n'.join(table[:3])
        foot = table[-1]
        start = 0
        table = table[3:]
        for pos, name in sorted(sections.items()):
            section_head = '{}\x1b(B{}\x1b(0{}'.format(head[:start_size], name, head[start_size+len(name):])
            table_splitted.append(section_head)
            table_splitted.append('\n'.join(table[start:pos]))
            table_splitted.append(foot)
            enabled = self.sma.monitors.is_monitor_enabled(name)
            last_execution = self.sma.monitors_info.get(name, {}).get('last_execution')
            table_splitted.append('Enabled: {} Last update: {}\n'.format(
                getattr(Color, 'green' if enabled else 'red')(enabled),
                human_since(last_execution, True) if last_execution else '??'
            ))
            start = pos
        return '\n'.join(table_splitted)

    def __repr__(self):
        return self.__str__()


class MonitorsInfo(JSONFile):
    def get_monitor(self, monitor, create=True):
        if monitor.name not in self and create:
            self[monitor.name] = {'headers': {}, 'last_execution': None}
        return self.get(monitor.name)

    def set_headers(self, monitor, headers):
        for key, value in headers.items():
            if value.isdigit():
                value = int(value)
            headers[key] = value
        self.get_monitor(monitor)['headers'] = headers

    def set_last_execution(self, monitor):
        self.get_monitor(monitor)['last_execution'] = datetime.datetime.now(dateutil.tz.tzlocal()).isoformat()


class SMA(object):
    def __init__(self, monitors_dir=None, alerts_dir=None, config_file=None):
        # noinspection PyTypeChecker
        results_file = create_file(os.path.join(get_var_directory(), 'results.json'), {
            'version': __version__,
            'monitors': {},
        })
        self.config = Config(config_file)
        self.results = Results(results_file, sma=self)
        self.monitors_info = MonitorsInfo(os.path.join(get_var_directory(), 'monitors.json'))
        self.monitors = Monitors(monitors_dir, self.config, self)
        self.alerts = Alerts(self, alerts_dir)

    def evaluate_and_alert(self):
        observables = self.evaluate_all()
        fail_observables = [observable for (observable, result) in observables if not result]
        self.alert_all(fail_observables)

    def alert_all(self, observables, fail=True):
        for observable in observables:
            self.alerts.send_alerts(observable, fail)
        self.results.write()

    def execute_all(self):
        return self.monitors.execute_all()

    def evaluate_all(self):
        observables = self.execute_all()
        for observable in observables:
            result = observable.evaluate()
            self.results.update_observable_result(observable, not result)
            log_evaluate(observable, result)
            yield observable, result
        self.results.write()


class SMAService(SMA):
    def start(self):
        while True:
            start_t = time.time()
            self.evaluate_and_alert()
            wait = WAIT_SECONDS - (time.time() - start_t)
            time.sleep(wait if wait > 0 else 0)
