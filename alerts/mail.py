#!/usr/bin/env python
import sys
import smtplib
from simple_monitor_alert.alerts import AlertBase

__version__ = '0.1.0'

SUPPORT_ALERT_IMPORT = True


class Mail(AlertBase):
    bot = None
    telegram_cache = None

    def init(self):
        s = smtplib.SMTP('localhost')

    def send(self, subject, message, observable_name='', name='', extra_info=None, level='warning', fail=True,
             condition=''):
        pass

Alert = Mail
