# Отправка текущего состояния параметров аквариума в 10 и в 20 часов.
#
# Текущее состояние системы охлаждения аквариума:
# 🟢 Температура воды (подача): 9 °C
# 🔴 Температура воздуха 18 °C
# 🟢 Внешнее питание терминала в норме

import threading
from datetime import datetime, timedelta
import schedule
import time

import yaml

from plugins.storage_mysql import Storage
from plugins.telegram import Sender


class Aquarium:
    def __init__(self, p_config: dict, p_storage: Storage, p_sender: Sender):
        self.config = p_config
        self.sender = p_sender
        self.storage = p_storage
        self.chat_id = p_config['telegram']['chat_id']
        self.final_message = "Текущее состояние системы охлаждения аквариума:\n"
        self.device_id = 4

    # Возвращает состояние параметра в человекочитаемом виде
    # и необходимость внимания (True - требует внимания, False - норма)
    def get_param_state_and_alert(self, parameter_id: int, messages: dict) -> (str, bool):
        p = self.storage.get_line("""
            SELECT id, parameter_id, event_id, current_value, min_value, max_value,
                 `datetime`, timeout, no_data_message,
                 below_min_message, above_max_message, 
                 `alert`, triggered, chat_id
                 FROM monitoring WHERE device_id = %s AND parameter_id = %s
                 """,
                                  [self.device_id, parameter_id])

        timeout = 3600 if p['timeout'] is None else p['timeout']
        no_data_message = 'Нет данных длительное время' if p['no_data_message'] is None else p['no_data_message']
        if p['datetime'] is None or p['datetime'] < datetime.now() - timedelta(seconds=timeout):
            return no_data_message, True
        value_str = str(round(p['current_value']))
        if p['current_value'] < p['min_value']:
            return messages['below'].replace('%VALUE%', value_str), True
        elif p['current_value'] > p['max_value']:
            return messages['above'].replace('%VALUE%', value_str), True
        else:
            return messages['normal'].replace('%VALUE%', value_str), False

    def send_notification(self):
        disable_notification = True  # Сообщение в Телеграм отправлять со звуковым уведомлением

        info, alert = self.get_param_state_and_alert(49, {'normal': '🟢 Температура воды (подача): %VALUE% °C',
                                                          'below': '🔴 Температура воды (подача) : %VALUE% °C',
                                                          'above': '🔴 Температура воды (подача) : %VALUE% °C',
                                                          })
        final_message = self.final_message + info + '\n'
        if alert:
            disable_notification = False

        info, alert = self.get_param_state_and_alert(51, {'normal': '🟢 Температура воздуха: %VALUE% °C',
                                                          'below': '🔴 Температура воздуха: %VALUE% °C',
                                                          'above': '🔴 Температура воздуха: %VALUE% °C',
                                                          })
        final_message += info + '\n'
        if alert:
            disable_notification = False

        info, alert = self.get_param_state_and_alert(19, {'normal': '🟢 Внешнее питание терминала в норме',
                                                          'below': '🔴 Внешнее питание терминала ниже нормы',
                                                          'above': '🔴 Внешнее питание терминала выше нормы',
                                                          })
        final_message += info + '\n'
        if alert:
            disable_notification = False

        self.sender.send_message(self.chat_id, final_message, disable_notification)

    def run(self):
        schedule.every().day.at("10:00").do(self.send_notification)
        schedule.every().day.at("20:00").do(self.send_notification)
        while True:
            schedule.run_pending()
            time.sleep(10)

    def run_test(self):
        schedule.every(1).minutes.do(self.send_notification)
        while True:
            schedule.run_pending()
            time.sleep(10)


if __name__ == '__main__':
    with open('config/config.yml', "r", encoding="utf-8") as stream:
        config = yaml.safe_load(stream)

    sender = Sender(config['telegram'])
    storage = Storage(config)
    aquarium = Aquarium(config, storage, sender)
    threading.Thread(target=aquarium.run_test).start()
