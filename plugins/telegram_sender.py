# Плагин отправки уведомлений в телеграм.
from threading import Thread

import requests
from retrying import retry

from plugins.logger import log
from plugins.storage import Storage


def retry_if_io_error(exception):
    print(f"error: {exception}")
    return isinstance(exception, IOError)


class TelegramSender:
    def __init__(self, storage: Storage):
        self.bot_token = storage.get_system_param('telegram_bot_token')
        self.send_message_url = 'https://api.telegram.org/bot' + self.bot_token + '/sendMessage'

    # Отправка сообщения в Телеграм-чат.
    @retry(retry_on_exception=retry_if_io_error, wait_exponential_multiplier=1000, wait_exponential_max=10000)
    def send_message_with_retry(self, chat_id: int, text: str, disable_notification=False):
        log(f'TELEGRAM: Отправляем сообщение: chat_id: {chat_id}, text: {text}')
        request = {
            'chat_id': chat_id,
            'text': text,
            'disable_notification': disable_notification
        }
        response = requests.post(self.send_message_url, json=request)
        if response.status_code != 200:
            print(f'Error: {response.status_code} {response.text}')
            return
        j = response.json()
        if 'ok' not in j or 'result' not in j or 'message_id' not in j['result']:
            return


    # Отправка сообщения в отдельном потоке, чтобы не задерживать основной
    def send_message(self, chat_id: int, text: str, disable_notification=False):
        Thread(target=self.send_message_with_retry, args=(chat_id, text, disable_notification)).start()

