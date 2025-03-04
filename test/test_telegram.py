# Тестирование отправки сообщения ботом
import yaml

from plugins.telegram import Sender

with open('config/config.yml', "r", encoding="utf-8") as stream:
    config = yaml.safe_load(stream)
chat_id = 47254369
sender = Sender(config['telegram'])
sender.send_message(chat_id, "Проверка отправки сообщений без уведомлений", True)

