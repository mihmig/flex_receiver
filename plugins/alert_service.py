# Отправка уведомлений
from plugins.max_sender import MaxSender
from plugins.storage import Storage
from plugins.telegram_sender import TelegramSender


class AlertService:
    def __init__(self, storage: Storage, p_telegram_sender: TelegramSender, p_max_sender: MaxSender):
        self.storage = storage
        self.telegram_sender = p_telegram_sender
        self.max_sender = p_max_sender

    def send_alert(self, device: dict, param: dict, message: str) -> None:
        telegram_chat_id = param['telegram_chat_id'] or device['telegram_chat_id']
        if telegram_chat_id:
            self.telegram_sender.send_message(telegram_chat_id, message)

        max_chat_id = param['max_chat_id'] or device['max_chat_id']
        if max_chat_id:
            self.max_sender.send_message(max_chat_id, message)

    def send_alert_for_device(self, device: dict, message: str, disable_notification=False):
        telegram_chat_id = device['telegram_chat_id'] or self.storage.get_system_param('telegram_chat_id')
        if telegram_chat_id:
            self.telegram_sender.send_message(telegram_chat_id, message, disable_notification)

        max_chat_id = device['max_chat_id'] or self.storage.get_system_param('max_chat_id')
        if max_chat_id:
            self.max_sender.send_message(max_chat_id, message)

