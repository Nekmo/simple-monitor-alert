#!/usr/bin/env python
import telegram
from simple_monitor_alert.alerts import AlertBase


SUPPORT_ALERT_IMPORT = True

class Telegram(AlertBase):
    bot = None

    def init(self):
        print(repr(self.config['token']))
        self.bot = telegram.Bot(token=self.config['token'])
        print(self.bot.getMe())
        updates = self.bot.getUpdates()
        # print([vars(u.message.chat) for u in updates])

    def search_uid(self, name):
        if isinstance(name, int):
            return name
        for update in self.bot.getUpdates():
            if '@{}'.format(update.message.from_user.username) == name:
                return update.message.from_user.id
        return name

    def send(self, to, name, result, extra_info=None, level='warning', resolved=False):
        to = self.search_uid(to)
        self.bot.sendMessage(chat_id=to, text="I'm sorry Dave I'm afraid I can't do that.")

if __name__ == '__main__':
    # Telegram().send(14390491, '', '')
    Telegram().send('@nekmo', '', '')
