# Плагин отправки уведомлений в телеграм.
from threading import Thread

import requests
from retrying import retry


def retry_if_io_error(exception):
    return isinstance(exception, IOError)


class Sender:
    def __init__(self, config: dict):
        self.config = config
        self.bot_token = config['bot_token']

    # Отправка сообщения в Телеграм-чат.
    @retry(retry_on_exception=retry_if_io_error, wait_exponential_multiplier=1000, wait_exponential_max=10000)
    def send_message_with_retry(self, user_info: str, chat_id: int, text: str):
        request = {
            'chat_id': chat_id,
            'text': text
        }
        response = requests.post('https://api.telegram.org/bot' + self.bot_token + '/sendMessage', json=request)
        if response.status_code != 200:
            print(f'Error: {response.status_code} {response.text}')
            return
        j = response.json()
        if 'ok' not in j or 'result' not in j or 'message_id' not in j['result']:
            return

    # Отправка сообщения в отдельном потоке, чтобы не задерживать основной
    def send_message(self, user_info: str, chat_id: int, text: str):
        Thread(target=self.send_message_with_retry, args=(user_info, chat_id, text,)).start()

