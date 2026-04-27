# Отправка текущего состояния параметров аквариума в 10 и в 20 часов.
#
# Текущее состояние системы охлаждения аквариума:
# 🟢 Температура воды (подача): 9 °C
# 🔴 Температура воздуха 18 °C
# 🟢 Внешнее питание терминала в норме

from datetime import datetime, timedelta
import schedule

from plugins.alert_service import AlertService
from plugins.max_sender import MaxSender
from plugins.storage import Storage
from plugins.telegram_sender import TelegramSender


class Aquarium:
    def __init__(self, p_storage: Storage, p_alert_service: AlertService):
        self.storage = p_storage
        self.alert_service = p_alert_service
        self.final_message = "Текущее состояние системы охлаждения аквариума:\n"
        self.device_id = 4
        schedule.every().day.at("10:00").do(self.send_notification)
        schedule.every().day.at("20:00").do(self.send_notification)

    # Возвращает состояние параметра в человекочитаемом виде
    # и необходимость внимания (True - требует внимания, False - норма)
    def get_param_state_and_alert(self, parameter_id: int, messages: dict) -> (str, bool):
        p = self.storage.get_line("""
            SELECT id, parameter_id, event_id, current_value, min_value, max_value,
                 `datetime`, timeout, no_data_message,
                 below_min_message, above_max_message, 
                 `alert`, triggered, telegram_chat_id, max_chat_id
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

        device = self.storage.get_line("SELECT * FROM device WHERE id = %s", [self.device_id])
        self.alert_service.send_alert_for_device(device, final_message, disable_notification)


if __name__ == '__main__':
    storage = Storage()
    telegram_sender = TelegramSender(storage)
    max_sender = MaxSender(storage)
    alert_service = AlertService(storage, telegram_sender, max_sender)
    aquarium = Aquarium(storage, alert_service)
    # schedule.every(1).minutes.do(aquarium.send_notification)
    aquarium.send_notification()
    # while True:
    #     schedule.run_pending()
    #     time.sleep(10)
