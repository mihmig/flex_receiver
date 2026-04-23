# Плагин отправки уведомлений в телеграм.
from threading import Thread

import requests
from retrying import retry

from plugins.logger import log
from plugins.storage_mysql import Storage


def retry_if_io_error(exception):
    print(f"error: {exception}")
    return isinstance(exception, IOError)


class MaxSender:
    def __init__(self, storage: Storage):
        self.storage = storage
        self.send_message_url = "https://platform-api.max.ru/messages"
        self.headers = {
            "Authorization": storage.get_system_param('max_bot_token'),
            "Content-Type": "application/json"
        }


    # Отправка сообщения в Телеграм-чат.
    @retry(retry_on_exception=retry_if_io_error, wait_exponential_multiplier=1000, wait_exponential_max=10000)
    def send_message_with_retry(self, chat_id: int, text: str):
        log(f'MAX: Отправляем сообщение: chat_id: {chat_id}, text: {text}')
        params = {
            "chat_id": chat_id
        }
        response = requests.post(self.send_message_url,
                                 params=params,
                                 headers=self.headers,
                                 json={"text": text}
                                 )

        if response.status_code != 200:
            log(f'Error: {response.status_code} {response.text}')



    # Отправка сообщения в отдельном потоке, чтобы не задерживать основной
    def send_message(self, chat_id: int, text: str):
        Thread(target=self.send_message_with_retry, args=(chat_id, text)).start()


