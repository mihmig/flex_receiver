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
    def send_message_with_retry(self, chat_id: int, text: str, disable_notification=False):
        request = {
            'chat_id': chat_id,
            'text': text,
            'disable_notification': disable_notification
        }
        response = requests.post('https://api.telegram.org/bot' + self.bot_token + '/sendMessage', json=request)
        if response.status_code != 200:
            print(f'Error: {response.status_code} {response.text}')
            return
        j = response.json()
        if 'ok' not in j or 'result' not in j or 'message_id' not in j['result']:
            return
        print(response.text)

    # Отправка сообщения в отдельном потоке, чтобы не задерживать основной
    def send_message(self, chat_id: int, text: str, disable_notification=False):
        Thread(target=self.send_message_with_retry, args=(chat_id, text, disable_notification)).start()

    def delete_message(self, chat_id: int, message_id: int):
        request = {
            'chat_id': chat_id,
            'message_id': message_id
        }
        response = requests.post('https://api.telegram.org/bot' + self.bot_token + '/deleteMessage', json=request)
        print(response.text)
