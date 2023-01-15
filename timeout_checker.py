# Проверка на поступление параметров.
# Отправляет сообщение в телеграм, если параметр не поступал дольше определённого времени
from datetime import datetime
from time import sleep

from config import config
from plugins.storage_mysql import Storage
from telegram import Sender


class Checker():
    def __init__(self, config: dict, storage: Storage, sender: Sender):
        self.config = config
        self.sender = sender
        self.chat_id = config['telegram']['chat_id']
        self.storage = Storage(config)

    def check(self):
        while True:
            params = self.storage.get_data("SELECT id, parameter_id, event_id, min_value, max_value, `datetime`, "
                                           "timeout, triggered, chat_id"
                                           " FROM monitoring WHERE alert = true and triggered = false")
            now = datetime.now()
            for p in params:
                timeout = p.get('timeout') or config['default_timeout']
                # Проверяем - давно ли появлялся такой параметр
                last_data = p.get('datetime')
                if not last_data:
                    continue  # Никогда не появлялся
                interval = round((now - last_data).total_seconds())
                if interval > timeout:
                    parameter_description = self.storage.get_parameter_description(p['parameter_id'])
                    self.sender.send_message(p.get('chat_id') or self.chat_id,
                                             f"Параметр '{parameter_description}' не поступал уже более {interval} с.")
                    self.storage.execute("UPDATE monitoring SET triggered = true WHERE id = %s", [p['id']])
            sleep(60)
