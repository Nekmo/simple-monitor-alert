#!/usr/bin/env python
__version__ = '0.1.0'

import os

import datetime
import telebot
import sys
import six
import dateutil
import dateutil.tz


from simple_monitor_alert.sma import create_file, get_var_directory, JSONFile

if sys.version_info >= (3,2):
    from html import escape
else:
    from cgi import escape

from simple_monitor_alert.alerts import AlertBase


SUPPORT_ALERT_IMPORT = True


class Mail(AlertBase):
    bot = None
    telegram_cache = None

    def init(self):
        token = self.config.get('token')
        self.bot = telebot.TeleBot(token)
        self.telegram_cache = JSONFile(create_file(os.path.join(get_var_directory(), 'telegram-cache.json'), {
            'chat_ids': {},
            'version': __version__,
        }))
        # print([vars(u.message.chat) for u in updates])

    def search_uid(self, name):
        if name in self.telegram_cache['chat_ids']:
            return self.telegram_cache['chat_ids'][name]['id']
        if isinstance(name, int):
            return name
        for update in self.bot.get_updates():
            if '@{}'.format(update.message.from_user.username) == name:
                self.telegram_cache['chat_ids'][name] = {
                    'id': update.message.from_user.id,
                    'updated_at': datetime.datetime.now(dateutil.tz.tzlocal()).isoformat()
                }
                self.telegram_cache.write()
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
        return True

Alert = Mail
