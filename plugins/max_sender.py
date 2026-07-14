# Плагин отправки уведомлений в телеграм.
from threading import Thread

import requests
from retrying import retry

from plugins.logger import log
from plugins.storage import Storage


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
        self.prefix = storage.get_system_param('message_prefix_max')


    # Отправка сообщения в MAX-чат.
    @retry(retry_on_exception=retry_if_io_error,
           wait_exponential_multiplier=1000,
           wait_exponential_max=10000,
           stop_max_attempt_number=3,
           stop_max_delay=60000
           )
    def send_message_with_retry(self, p_chat_id: int, p_text: str):
        text = self.prefix + p_text if self.prefix else p_text
        log(f'MAX: Отправляем сообщение: chat_id: {p_chat_id}, text: {text}')
        params = {
            "chat_id": p_chat_id
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


