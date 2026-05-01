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

    def get_param_state_and_alert(self, parameter_id: int, messages: dict) -> (str, bool):
        """
        Возвращает состояние параметра в человекочитаемом виде
        и необходимость внимания (True - требует внимания, False - норма)
        :param parameter_id: идентификатор параметра
        :param messages: набор из 3-х шаблонов сообщений (для случаев, когда параметр ниже, в норме или выше нормы)
        :return: итоговое состояние и признак - требуется ли звуковое оповещение
        (если параметр в норме, то звуковое оповещение не требуется)
        """

        param = self.storage.get_device_monitoring_param(self.device_id, parameter_id)

        timeout = 3600 if param['timeout'] is None else param['timeout']
        no_data_message = 'Нет данных длительное время' if param['no_data_message'] is None else param['no_data_message']
        if param['datetime'] is None or param['datetime'] < datetime.now() - timedelta(seconds=timeout):
            return no_data_message, True
        value_str = str(round(param['current_value']))
        if param['current_value'] < param['min_value']:
            return messages['below'].replace('%VALUE%', value_str), True
        elif param['current_value'] > param['max_value']:
            return messages['above'].replace('%VALUE%', value_str), True
        else:
            return messages['normal'].replace('%VALUE%', value_str), False

    def send_notification(self) -> None:
        """
        Отправка текущего статуса параметров аквариума
        """
        if not self.storage.get_system_param('aquarium_send') == 'true':
            return

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
