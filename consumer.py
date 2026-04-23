# Модуль обработки FLEX-пакетов данных
import json
from datetime import datetime
from constants import *
from plugins.monitoring_service import MonitoringService
from plugins.storage_mysql import Storage
from plugins.logger import log


class Consumer:
    def __init__(self, storage: Storage, p_monitoring_service: MonitoringService):
        self.storage = storage
        self.monitoring_service = p_monitoring_service

    def consume_flex_message(self, imei: str, packet_type: str, data: bytes | None, decoded: dict | None):
        """ Обрабатывает декодированное FLEX-сообщение"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        device_id, new = self.storage.get_device_id_by_imei(imei)
        if new:
            log(f"Новое устройство. IMEI={imei}")
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
            self.monitoring_service.do_monitoring(device_id, decoded)
        elif packet_type == PACKET_TYPE_ERROR:
            self.storage.save_message(device_id, 0, now, packet_type, data, json.dumps(decoded))
        else:
            log(f'Unknown packet type: {packet_type}')

    def debug_message(self, device_id: str, packet_type: str, message: dict):
        """ Выводит отдельные поля сообщения в консоль """
        f = []
        for i in self.storage.get_param_list('fields_to_show'):
            if i in message:
                f.append(message[i])
            else:
                f.append('~')
        formatted_line = '\t'.join(str(x) for x in f)
        log(f"{packet_type} {device_id} {formatted_line}")
