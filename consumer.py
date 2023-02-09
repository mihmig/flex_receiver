# Модуль хранения пакетов данных
import json
from datetime import datetime
from constants import *
from plugins.storage_mysql import Storage
from logger import log
from telegram import Sender


class Consumer:
    def __init__(self, config: dict, storage: Storage, sender: Sender):
        self.config = config
        self.fields_to_show = config['fields_to_show']
        self.storage = storage
        self.sender = sender
        self.chat_id = config['telegram']['chat_id']
        # Кеш устройств
        self.devices = {}

    # Контроль параметров на выход за установленные рамки и возвращение в норму
    def do_monitoring(self, device_id: int, decoded: dict):
        moment_str = decoded.get(EVENT_TIME_FIELD)
        moment = datetime.strptime(moment_str, "%Y-%m-%d %H:%M:%S")
        params = self.storage.get_data("SELECT id, parameter_id, event_id, min_value, max_value, `datetime`, timeout,"
                                       " below_min_message, above_max_message, in_range_message, "
                                       " `alert`, triggered, chat_id"
                                       " FROM monitoring WHERE device_id = %s", [device_id])
        now = datetime.now()
        for p in params:
            id = p['id']
            parameter_id = p.get('parameter_id')
            value = decoded.get(str(parameter_id))
            if value is None:
                continue  # В полученных данных нет данного параметра
            self.storage.execute("UPDATE monitoring SET `datetime` = %s, current_value = %s WHERE id = %s",
                                 [now, value, id])

            # Проверки на выход параметра за пределы и возврат в норму
            if value < p['min_value']:
                if not p['triggered']:
                    self.storage.execute("UPDATE monitoring SET triggered = true WHERE id = %s", [id])
                    if p.get('alert'):
                        if p['below_min_message']:
                            message = p['below_min_message'].replace("%VALUE%", str(value)) \
                                .replace("%MOMENT%", str(moment_str))
                        else:
                            parameter_description = self.storage.get_parameter_description(parameter_id)
                            message = f"Значение параметра '{parameter_description}' " \
                                      f"на {moment_str} ({value}) " \
                                      f"меньше допустимого {p['min_value']}"
                        self.sender.send_message(p.get('chat_id') or self.chat_id, message)

            elif value > p['max_value']:
                if not p['triggered']:
                    self.storage.execute("UPDATE monitoring SET triggered = true WHERE id = %s", [id])
                    if p.get('alert'):
                        if p['above_max_message']:
                            message = p['above_max_message'].replace("%VALUE%", str(value)) \
                                .replace("%MOMENT%", str(moment_str))
                        else:
                            parameter_description = self.storage.get_parameter_description(parameter_id)
                            message = f"Значение параметра '{parameter_description}' " \
                                      f"на {moment_str} ({value}) " \
                                      f"больше допустимого {p['max_value']}"
                        self.sender.send_message(p.get('chat_id') or self.chat_id, message)
            else:
                if p['triggered']:
                    # Параметр вернулся в норму (TODO предусмотреть гистерезис)
                    self.storage.execute("UPDATE monitoring SET triggered = false WHERE id = %s", [id])
                    if p.get('alert'):
                        if p.get('in_range_message'):
                            message = p['in_range_message'].replace("%VALUE%", str(value)) \
                                .replace("%MOMENT%", str(moment_str))
                        else:
                            parameter_description = self.storage.get_parameter_description(parameter_id)
                            message = f"Значение параметра '{parameter_description}' " \
                                      f"на {moment_str} ({value}) вернулось в норму"
                        self.sender.send_message(p.get('chat_id') or self.chat_id, message)

    # Обрабатывает FLEX-сообщение
    def consume_flex_message(self, imei: str, packet_type: str, data: bytes | None, decoded: dict | None):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if imei in self.devices:
            device_id = self.devices[imei]
        else:
            device_id, new = self.storage.get_device_id_by_imei(imei)
            if new:
                self.sender.send_message(self.chat_id, f"Новое устройство. IMEI={imei}")
            self.devices[imei] = device_id

        if packet_type == PACKET_TYPE_PING:
            self.storage.update_last_alive(device_id)
            log(f'{imei}: consumed PING')
        elif packet_type == PACKET_TYPE_HANDSHAKE:
            self.storage.update_last_alive(device_id)
            self.storage.save_message(device_id, 0, now, packet_type, data, None)
            log(f'{imei}: consumed HANDSHAKE')
        elif packet_type == PACKET_TYPE_APPROVAL:
            self.storage.save_message(device_id, 0, now, packet_type, data, None)
            log('consumed PACKET_TYPE_APPROVAL')
        elif packet_type == PACKET_TYPE_A or packet_type == PACKET_TYPE_C or packet_type == PACKET_TYPE_T:
            self.storage.update_last_alive(device_id)
            self.debug_message(imei, packet_type, decoded)
            event_id = decoded['2']
            event_time = decoded['3']
            self.storage.save_message(device_id, event_id, event_time, packet_type, data, json.dumps(decoded))
            self.do_monitoring(device_id, decoded)
        elif packet_type == PACKET_TYPE_ERROR:
            self.storage.save_message(device_id, 0, now, packet_type, data, json.dumps(decoded))
        else:
            log(f'Unknown packet type: {packet_type}')

    # Выводит отдельные поля сообщения в консоль
    def debug_message(self, client_id: str, packet_type: str, message: dict):
        f = []
        for i in self.fields_to_show:
            if i in message:
                f.append(message[i])
            else:
                f.append('~')
        formatted_line = '\t'.join(str(x) for x in f)
        log(f"{packet_type} {client_id} {formatted_line}")
