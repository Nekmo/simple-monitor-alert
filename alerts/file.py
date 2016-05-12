#!/usr/bin/env python
import sys
import smtplib
from email.mime.text import MIMEText

from simple_monitor_alert.alerts import AlertBase
from simple_monitor_alert.monitor import log_evaluate

__version__ = '0.1.0'

SUPPORT_ALERT_IMPORT = True


class File(AlertBase):
    path = None

    def init(self):
        self.path = self.config.get('path')

    def send(self, subject, message, observable=None, result=None, **kwargs):
        line = log_evaluate(observable, result, False)
        with open(self.path, 'a') as f:
            f.write('{}\n'.format(line))
        return True


Alert = File
