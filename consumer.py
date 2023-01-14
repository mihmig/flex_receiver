# Модуль хранения пакетов данных
import json
from datetime import datetime
from constants import PACKET_TYPE_PING, PACKET_TYPE_A, PACKET_TYPE_C, PACKET_TYPE_HANDSHAKE, PACKET_TYPE_APPROVAL, \
    PACKET_TYPE_T, PACKET_TYPE_ERROR
from plugins.storage_mysql import Storage
from logger import log
from telegram import Sender


class Consumer:
    def __init__(self, config: dict, sender: Sender):
        self.config = config
        self.fields_to_show = config['fields_to_show']
        self.storage = Storage(config)
        self.sender = sender
        self.chat_id = config['telegram']['chat_id']
        # Кеш устройств
        self.devices = {}

    # Обрабатывает полученные данные
    # (выясняет - не вышел ли какой из параметров устройства за пределы)
    def do_monitoring(self, device_id: int, decoded: dict):
        params = self.storage.get_data("SELECT id, parameter_id, event_id, min_value, max_value, alert"
                                       " FROM monitoring WHERE device_id = %s", [device_id])
        for p in params.values():
            pass

    # Обрабатывает FLEX-сообщение
    def consume_flex_message(self, imei: str, packet_type: str, data: bytes | None, decoded: dict | None):
        now = datetime.now().strftime("%Y-%d-%m %H:%M:%S")
        if imei in self.devices:
            device_id = self.devices[imei]
        else:
            device_id, new = self.storage.get_device_id_by_imei(imei)
            if new:
                self.sender.send_message(imei, self.chat_id, f"Новое устройство. IMEI={imei}")
            self.devices[imei] = device_id

        if packet_type == PACKET_TYPE_PING:
            self.storage.update_last_alive(device_id)
            self.storage.save_message(device_id, 0, now, packet_type, None, None)
            log(f'{imei}: consumed PING')
        elif packet_type == PACKET_TYPE_HANDSHAKE:
            self.storage.update_last_alive(device_id)
            self.storage.save_message(device_id, 0, now, packet_type, data, None)
            log(f'{imei}: consumed HANDSHAKE')
        elif packet_type == PACKET_TYPE_APPROVAL:
            self.storage.save_message(device_id, 0, now, packet_type, data, None)
            log('consumed PACKET_TYPE_APPROVAL')
        elif packet_type == PACKET_TYPE_A:
            self.debug_message(imei, packet_type, decoded)
            event_id = decoded['2']
            event_time = decoded['3']
            self.storage.save_message(device_id, event_id, event_time, packet_type, data, json.dumps(decoded))
        elif packet_type == PACKET_TYPE_C:
            self.debug_message(imei, packet_type, decoded)
            event_id = decoded['2']
            event_time = decoded['3']
            self.storage.save_message(device_id, event_id, event_time, packet_type, data, json.dumps(decoded))
        elif packet_type == PACKET_TYPE_T:
            self.debug_message(imei, packet_type, decoded)
            event_id = decoded['2']
            event_time = decoded['3']
            self.storage.save_message(device_id, event_id, event_time, packet_type, data, json.dumps(decoded))
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
