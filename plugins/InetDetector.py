# Контролирует наличие интернета (данные от трекера поступают не реже, чем раз в 5 минут)
import threading
from datetime import datetime
import time

import requests
import schedule
import yaml

from plugins.storage_mysql import Storage


class InetDetector:
    def __init__(self, p_config: dict, p_storage: Storage):
        self.config = p_config
        self.storage = p_storage
        self.device_id = 8
        self.url = "https://platform-api.max.ru/messages"
        self.params = {
            "chat_id": p_config['max']['chat_id']
        }
        self.headers = {
            "Authorization": p_config['max']['bot_token'],
            "Content-Type": "application/json"
        }
        self.state = 'ONLINE'

    def send_message(self, message: str):
        print(f'отправляем сообщение: message')
        requests.post(self.url,
                      params=self.params,
                      headers=self.headers,
                      json={"text": message}
                      )

    def get_device_data(self, device_id: int) -> dict:
        return self.storage.get_line("""
            SELECT id, last_alive, timeout, timeout_message, online_message, state 
            FROM device
            WHERE id = %s
        """, [device_id])

    def check_inet(self):
        print('Проверяем статус')
        now = datetime.now()
        d = self.get_device_data(self.device_id)
        last_alive = d.get('last_alive')
        timeout = d.get('timeout')

        interval = round((now - last_alive).total_seconds())
        if d.get('state') is None or d.get('state') == 'ONLINE':
            if interval > timeout:
                self.send_message(d['timeout_message'])
                self.storage.execute("UPDATE device SET state = %s WHERE id = %s", ['OFFLINE', d['id']])
            elif d.get('state') is None:
                self.storage.execute("UPDATE device SET state = %s WHERE id = %s", ['ONLINE', d['id']])
        elif d.get('state') == "OFFLINE":
            if interval < timeout:
                self.send_message(d['online_message'])
                self.storage.execute("UPDATE device SET state = %s WHERE id = %s", ['ONLINE', d['id']])

    def run(self):
        schedule.every(1).minute.do(self.check_inet)
        while True:
            n = schedule.idle_seconds()
            if n is None:
                time.sleep(30)
            elif n > 0:
                time.sleep(n)
            schedule.run_pending()


if __name__ == '__main__':
    with open('config/config.yml', "r", encoding="utf-8") as stream:
        config = yaml.safe_load(stream)

    storage = Storage(config)
    inet_detector = InetDetector(config, storage)
    threading.Thread(target=inet_detector.run).start()
