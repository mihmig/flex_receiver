# Проверки:
# 1. На то, онлайн у стройство или офлайн.
# 2. На поступление параметров от устройства.
# Отправляет сообщение в телеграм, если параметр не поступал дольше определённого времени
# и когда параметр снова начал обновляться
import time
from datetime import datetime

import schedule

from constants import DEVICE_STATE_ONLINE, DEVICE_STATE_OFFLINE
from plugins.alert_service import AlertService
from plugins.max_sender import MaxSender
from plugins.storage_mysql import Storage
from plugins.telegram_sender import TelegramSender


def get_device_name(device: dict) -> str:
    """ Возвращает имя устройства """
    name = f"Устройство: id={device.get('id') or ''}, imei={device.get('imei') or ''}," \
           f" name={device.get('name') or ''} ({device.get('comment') or ''})"
    return name


def get_device_offline_message(device: dict, interval: int):
    """ Формирует сообщение, когда устройство снова появилось. """
    return device.get('timeout_message') or f"Устройство '{get_device_name(device)}' не выходило на связь {interval} с."


def get_device_online_message(device: dict):
    """ Формирует сообщение, когда устройство долго не появлялось. """
    return device.get('online_message') or f"{get_device_name(device)} снова онлайн!"


class Checker:
    def __init__(self, p_storage: Storage, p_alert_service: AlertService):
        self.storage = p_storage
        self.alert_service = p_alert_service
        schedule.every(1).minute.do(self.check)

    def get_param_offline_message(self, param: dict):
        """ Формирует сообщение, когда параметр долго не появлялся. """
        pass


    def check(self) -> None:
        """ Проверяет - как давно устройство выходило на связь, и передавало те или иные параметры """
        devices = self.storage.get_dictionary("""
            SELECT id, imei, `name`, `comment`, last_alive, timeout, state, timeout_message, online_message,
                   telegram_chat_id, max_chat_id
            FROM device 
            WHERE state IS NOT NULL 
              AND state NOT IN ('ERROR', 'STOPPED')
              AND last_alive IS NOT NULL
        """)
        # Проверяем состояния устройств
        device_states = {}
        now = datetime.now()
        for device in devices.values():
            interval = round((now - device.get('last_alive')).total_seconds())
            if device.get('state') == DEVICE_STATE_ONLINE:
                timeout = device.get('timeout') or self.storage.get_system_param('device_default_timeout')
                if interval > timeout:
                    message = get_device_offline_message(device, interval)
                    self.alert_service.send_alert_for_device(device, message)
                    self.storage.update_device_state(device, DEVICE_STATE_OFFLINE)
                    device_states[device['id']] = DEVICE_STATE_OFFLINE
            elif device.get('state') == DEVICE_STATE_OFFLINE:
                # Устройство выходило на связь не далее, как 5 минут назад - считаем, что оно "Онлайн"
                if interval < 300:
                    message = get_device_online_message(device)
                    self.alert_service.send_alert_for_device(device, message)
                    self.storage.update_device_state(device, DEVICE_STATE_ONLINE)
                    device_states[device['id']] = DEVICE_STATE_ONLINE

        # Проверяем - как давно поступали параметры устройств
        # Для оффлайн-устройств отслеживание параметров не имеет смысла
        params = self.storage.get_dictionary("""
           SELECT m.id, m.device_id, parameter_id, event_id, min_value, max_value, `datetime`,
           m.timeout, no_data_message, data_resumption_message, m.alert,
           m.triggered_timeout, m.telegram_chat_id, m.max_chat_id
           FROM monitoring m
           JOIN device d ON d.id = m.device_id AND d.alert = true AND d.state = 'ONLINE' 
           WHERE m.alert = true
        """)
        now = datetime.now()
        for param in params.values():
            # Проверяем - давно ли появлялся такой параметр
            last_data = param.get('datetime')
            interval = round((now - last_data).total_seconds())
            timeout = param.get('timeout') or self.storage.get_system_param('device_default_timeout')
            if interval > timeout:
                if param.get('triggered_timeout'):
                    continue
                if param.get('no_data_message'):
                    message = param.get('no_data_message').replace("%TIMEOUT%", str(timeout // 60))
                else:
                    parameter_description = self.storage.get_parameter_description(param['parameter_id'])
                    message = f"Параметр '{parameter_description}' не поступал уже более {interval // 60} мин."
                self.alert_service.send_alert(devices[param['device_id']], param, message)
                self.storage.execute("UPDATE monitoring SET triggered_timeout = true WHERE id = %s", [param['id']])
                continue

            if not param.get('triggered_timeout'):
                continue
            if param.get('data_resumption_message'):
                message = param.get('data_resumption_message')
            else:
                parameter_description = self.storage.get_parameter_description(param['parameter_id'])
                message = f"Параметр '{parameter_description}' снова поступает"
            self.alert_service.send_alert(devices[param['device_id']], param, message)
            self.storage.execute("UPDATE monitoring SET triggered_timeout = false WHERE id = %s", [param['id']])


if __name__ == '__main__':
    storage = Storage()
    telegram_sender = TelegramSender(storage)
    max_sender = MaxSender(storage)
    alert_service = AlertService(storage, telegram_sender, max_sender)
    checker = Checker(storage, alert_service)
    checker.check()
    while True:
        schedule.run_pending()
        time.sleep(10)