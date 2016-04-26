#!/usr/bin/env python
import telebot
import sys
import six

if sys.version_info >= (3,2):
    from html import escape
else:
    from cgi import escape

from simple_monitor_alert.alerts import AlertBase


SUPPORT_ALERT_IMPORT = True
DEFAULT_MESSAGE = """\
%(icon)b [{level}] Simple-Monitor-Alert
 <strong>{name}</strong>
{extra_info}

Observable: {observable_name}
{condition_status} condition: {condition}
"""


LEVELS = {
    None: b'\xE2\x9C\x85',  # Resolved
    'info': b'\xE2\x84\xB9',
    'warning': b'\xF0\x9F\x94\xB4',
    'average': b'\xE2\x9D\x8C',
    'high': b'\xE2\x9D\x97',
    'disaster': b'\xE2\x80\xBC',
}

class Telegram(AlertBase):
    bot = None

    def init(self):
        token = self.config.get('token')
        self.bot = telebot.TeleBot(token)
        # print([vars(u.message.chat) for u in updates])

    def search_uid(self, name):
        if isinstance(name, int):
            return name
        for update in self.bot.get_updates():
            if '@{}'.format(update.message.from_user.username) == name:
                return update.message.from_user.id
        return name

    def send(self, subject, message, observable_name='', name='', extra_info=None, level='warning', fail=True,
             condition=''):
        to = self.search_uid(self.config['to'])
        icon = LEVELS.get(level)
        condition_status = 'Failed' if fail else 'Successful'
        level = level.upper()
        scope = locals()
        message = DEFAULT_MESSAGE.format(**{key: (escape(value) if isinstance(value, six.string_types) else value)
                                            for key, value in scope.items()})
        message = message.encode('utf-8')
        message = message % {b'icon': icon}
        self.bot.send_message(chat_id=to, text=message, parse_mode='HTML')

Alert = Telegram
