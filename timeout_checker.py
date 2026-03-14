# Проверки:
# 1. На то, онлайн у стройство или оффлайн.
# 2. На поступление параметров от устройства.
# Отправляет сообщение в телеграм, если параметр не поступал дольше определённого времени
# и когда параметр снова начал обновляться
import threading
from datetime import datetime

import schedule
import yaml

from plugins.logger import log
from plugins.storage_mysql import Storage
from plugins.telegram import Sender


# Возвращает имя устройства
def get_device_name(device: dict) -> str:
    name = f"Устройство: id={device.get('id') or ''}, imei={device.get('imei') or ''}," \
           f" name={device.get('name') or ''} ({device.get('comment') or ''})"
    return name


class Checker:
    def __init__(self, _config: dict, _storage: Storage, _sender: Sender):
        self.config = _config
        self.sender = _sender
        self.chat_id = _config['telegram']['chat_id']
        self.storage = _storage
        schedule.every(1).minute.do(self.check)

    def check(self) -> None:
        """
        Проверяет - как давно устройство выходило на связь, и передавало те или иные параметры
        """
        devices = self.storage.get_data("""
            SELECT id, imei, `name`, `comment`, last_alive, timeout, state, timeout_message, online_message, chat_id
            FROM device 
            WHERE (state <> 'ERROR' OR state IS NULL)  
            AND chat_id IS NOT NULL
        """)
        log(f'[{threading.get_ident()}] Проверяем статус устройств')
        device_states = {}
        now = datetime.now()
        for d in devices:
            last_alive = d.get('last_alive')
            if not last_alive:
                # Устройство ещё не подключалось
                continue
            interval = round((now - last_alive).total_seconds())
            if d.get('state') is None or d.get('state') == 'ONLINE':
                timeout = d.get('timeout') or self.config['device_default_timeout']
                if interval > timeout:
                    chat_id = d.get('chat_id') or self.chat_id
                    if d.get('timeout_message'):
                        message = d.get('timeout_message')
                    else:
                        message = f"{get_device_name(d)} не выходило на связь {interval} с."
                    self.sender.send_message(chat_id, message)
                    self.storage.execute("UPDATE device SET state = %s WHERE id = %s", ['OFFLINE', d['id']])
                elif d.get('state') is None:
                    self.storage.execute("UPDATE device SET state = %s WHERE id = %s", ['ONLINE', d['id']])
            elif d.get('state') == "OFFLINE":
                # Устройство выходило на связь не далее, как 5 минут назад
                if interval < 300:
                    chat_id = d.get('chat_id') or self.chat_id
                    if d.get('online_message'):
                        message = d.get('online_message')
                    else:
                        message = f"{get_device_name(d)} снова онлайн!"
                    self.sender.send_message(chat_id, message)
                    self.storage.execute("UPDATE device SET state = %s WHERE id = %s", ['ONLINE', d['id']])
            device_states[d.get('id')] = self.storage.get_value("SELECT state FROM device WHERE id = %s", [d['id']])
        # Параметры
        params = self.storage.get_data("""
           SELECT id, device_id, parameter_id, event_id, min_value, max_value, `datetime`,
           timeout, no_data_message, data_resumption_message, alert,
           triggered_timeout, chat_id
           FROM monitoring
           WHERE alert = true
        """)
        now = datetime.now()
        for p in params:
            if device_states.get(p['device_id']) != 'ONLINE':
                continue  # Для оффлайн-устройств отслеживание параметров не имеет смысла
            if not p.get('alert'):
                continue  # Параметр отслеживать не нужно
            # Проверяем - давно ли появлялся такой параметр
            last_data = p.get('datetime')
            if not last_data:
                continue  # Параметр ещё никогда не появлялся
            interval = round((now - last_data).total_seconds())
            timeout = p.get('timeout') or self.config['sensor_default_timeout']
            if interval > timeout:
                if p.get('triggered_timeout'):
                    continue
                if p.get('no_data_message'):
                    message = p.get('no_data_message').replace("%TIMEOUT%", str(timeout // 60))
                else:
                    parameter_description = self.storage.get_parameter_description(p['parameter_id'])
                    message = f"Параметр '{parameter_description}' не поступал уже более {interval // 60} мин."
                self.sender.send_message(p.get('chat_id') or self.chat_id, message)
                self.storage.execute("UPDATE monitoring SET triggered_timeout = true WHERE id = %s", [p['id']])
            else:
                if not p.get('triggered_timeout'):
                    continue
                if p.get('data_resumption_message'):
                    message = p.get('data_resumption_message')
                else:
                    parameter_description = self.storage.get_parameter_description(p['parameter_id'])
                    message = f"Параметр '{parameter_description}' снова поступает"
                self.sender.send_message(p.get('chat_id') or self.chat_id, message)
                self.storage.execute("UPDATE monitoring SET triggered_timeout = false WHERE id = %s", [p['id']])


if __name__ == '__main__':
    with open('config/config.yml', "r", encoding="utf-8") as stream:
        config = yaml.safe_load(stream)

    sender = Sender(config['telegram'])
    storage = Storage(config)
    checker = Checker(config, storage, sender)
    checker.check()
