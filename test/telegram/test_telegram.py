# Тестирование отправки сообщения ботом
from plugins.storage import Storage
from plugins.telegram_sender import TelegramSender

storage = Storage()
telegram_sender = TelegramSender(storage)

telegram_sender.send_message(47254369, "Проверка отправки сообщений без уведомлений", True)

