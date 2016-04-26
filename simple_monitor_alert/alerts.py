import os
import importlib
import logging

from future.moves import sys

from simple_monitor_alert.monitor import get_verbose_condition

logger = logging.getLogger('sma')


DEFAULT_MESSAGE = """\
{name}
{extra_info}

Observable: {observable_name}
{condition_status} condition: {condition}
"""

class AlertBase(object):
    def __init__(self, config):
        self.config = config
        self.init()

    def init(self):
        pass


class AlertCommand(AlertBase):
    pass


class Alerts(list):
    def __init__(self, config, alerts_dir):
        super(Alerts, self).__init__()
        self.config = config
        self.alerts_dir = alerts_dir
        sys.path.append(alerts_dir)
        self.valid_alerts = self.get_valid_alerts()
        self.get_alerts()

    def get_alerts_config(self):
        for section in self.config.sections():
            if self.config.has_option(section, 'alert'):
                alert = self.config.get(section, 'alert')
                if not alert in self.valid_alerts:
                    logger.warning('Invalid alert value {} for section {} in {}'.format(alert, section,
                                                                                        self.config.file))
            elif section in self.valid_alerts:
                alert = section
            else:
                continue
            yield alert, dict(self.config.items(alert))

    def _import_python_alert(self, alert, config):
        if not self.valid_alerts[alert].endswith('.py'):
            return
        module = importlib.import_module(alert)
        if getattr(module, 'SUPPORT_ALERT_IMPORT'):
            return getattr(module, 'Alert')(config)

    def _get_alert_command(self, alert, config):
        raise NotImplementedError

    def get_alerts(self):
        self.clear()
        for alert, alert_config in self.get_alerts_config():
            module = self._import_python_alert(alert, alert_config) or self._get_alert_command(alert, alert_config)
            self.append(module)

    def get_valid_alerts(self):
        return {os.path.splitext(f)[0]: os.path.join(self.alerts_dir, f) for f in os.listdir(self.alerts_dir)}

    def send_observable_result(self, observable, fail=True):
        subject = '[{}] {}'.format('ERROR' if fail else 'SOLVED', observable.get_verbose_name())
        name = observable.get_verbose_name()
        extra_info = observable.get_line_value('extra_info') or '(No more info available)'
        condition = get_verbose_condition(observable)
        message = DEFAULT_MESSAGE.format(name=name, observable_name=observable.name,
                                         extra_info=extra_info,
                                         condition=condition,
                                         condition_status='Failed' if fail else 'Successful')
        for alert in self:
            alert.send(subject, message, observable_name=observable.name, name=observable.get_verbose_name(),
                       extra_info=extra_info, level=observable.get_line_value('level', 'warning'), fail=fail,
                       condition=condition)
