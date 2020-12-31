#!/usr/bin/env python
import sys
import smtplib
from email.mime.text import MIMEText

from simple_monitor_alert.alerts import AlertBase

__version__ = '0.1.0'

SUPPORT_ALERT_IMPORT = True


class Mail(AlertBase):
    server = None

    def init(self):
        server = {
            'smtp': smtplib.SMTP, 'smtp-ssl': smtplib.SMTP_SSL, 'lmtp': smtplib.LMTP
        }[self.config.get('protocol', 'smtp').lower().replace('_', '-')]
        self.server = server(self.config.get('host', 'localhost'), self.config.get('port', 0))
        if self.config.get('start-tls', '').lower() in ['yes', 'true']:
            self.server.ehlo()
            self.server.starttls()
        user, password = self.config.get('user'), self.config.get('password')
        if user and password:
            self.server.login(user, password)

    def send(self, subject, message, observable_name='', name='', extra_info=None, level='warning', fail=True,
             condition='', hostname=None, observable=None):
        me = self.config.get('from', 'noreply@localhost')
        to = self.config.get('to', 'root@localhost')
        msg = MIMEText(message)
        msg['Subject'] = subject
        msg['From'] = me
        msg['To'] = to
        self.server.sendmail(me,[to], msg.as_string())
        return True

Alert = Mail
