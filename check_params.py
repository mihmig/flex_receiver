# Проверка на поступление параметров.
# Отправляет сообщение в телеграм, если параметр не поступал дольше определённого времени
from datetime import datetime

from config import config
from plugins.storage_mysql import Storage
from telegram import Sender

storage = Storage(config)
sender = Sender(config['telegram'])

params = storage.get_data("SELECT id, parameter_id, event_id, min_value, max_value, `datetime`, timeout,"
                          " triggered, chat_id"
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
        parameter_description = storage.get_parameter_description(p['parameter_id'])
        sender.send_message(p.get('chat_id') or config['telegram']['chat_id'],
                            f"Параметр '{parameter_description}' не поступал уже более {interval} с.")
        storage.execute("UPDATE monitoring SET triggered = true WHERE id = %s", [p['id']])
