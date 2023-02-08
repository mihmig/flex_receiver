# Проверка на поступление параметров.
# Отправляет сообщение в телеграм, если параметр не поступал дольше определённого времени
# и когда параметр снова начал обновляться
from datetime import datetime
from time import sleep

from config import config
from plugins.storage_mysql import Storage
from telegram import Sender


class Checker:
    def __init__(self, config: dict, storage: Storage, sender: Sender):
        self.config = config
        self.sender = sender
        self.chat_id = config['telegram']['chat_id']
        self.storage = storage

    def check(self):
        while True:
            params = self.storage.get_data("SELECT id, parameter_id, event_id, min_value, max_value, `datetime`,"
                                           " timeout, no_data_message, data_resumption_message, alert,"
                                           " triggered_timeout, chat_id"
                                           " FROM monitoring WHERE alert = true")
            now = datetime.now()
            for p in params:
                if not p.get('alert'):
                    continue  # Параметр отслеживать не нужно
                # Проверяем - давно ли появлялся такой параметр
                last_data = p.get('datetime')
                if not last_data:
                    continue  # Параметр ещё никогда не появлялся
                interval = round((now - last_data).total_seconds())
                timeout = p.get('timeout') or config['default_timeout']
                if interval > timeout:
                    if p.get('triggered_timeout'):
                        continue
                    if p.get('no_data_message'):
                        message = p.get('no_data_message').replace("%TIMEOUT%", str(timeout))
                    else:
                        parameter_description = self.storage.get_parameter_description(p['parameter_id'])
                        message = f"Параметр '{parameter_description}' не поступал уже более {interval} с."
                    self.sender.send_message(p.get('chat_id') or self.chat_id, message)
                    self.storage.execute("UPDATE monitoring SET triggered_timeout = true WHERE id = %s", [p['id']])
                elif interval < 300:  # Параметр обновился не далее, как 5 минут назад
                    if not p.get('triggered_timeout'):
                        continue
                    if p.get('data_resumption_message'):
                        message = p.get('data_resumption_message')
                    else:
                        parameter_description = self.storage.get_parameter_description(p['parameter_id'])
                        message = f"Параметр '{parameter_description}' снова поступает"
                    self.sender.send_message(p.get('chat_id') or self.chat_id, message)
                    self.storage.execute("UPDATE monitoring SET triggered_timeout = false WHERE id = %s", [p['id']])
            sleep(60)
