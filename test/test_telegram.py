# Тестирование отправки сообщения ботом
from telegram import Sender
from config import config

# chat_id = -1001882219961 # Inside оповещения
chat_id = 47254369
# chat_id = -868365203
# chat_id = 4129016 ## ksiop
sender = Sender(config['telegram'])
sender.send_message(chat_id, "Проверка отправки сообщений без уведомлений", True)
# sender.delete_message(chat_id, 106)
