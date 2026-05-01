# Модуль обработки FLEX-пакетов данных
import json
from datetime import datetime
from plugins.flex_constants import PACKET_TYPE_HANDSHAKE, PACKET_TYPE_APPROVAL, PACKET_TYPE_PING, PACKET_TYPE_A, \
    PACKET_TYPE_C, PACKET_TYPE_T, PACKET_TYPE_ERROR
from plugins.monitoring_service import MonitoringService
from plugins.spoofing_zone_filter import SpoofingZoneFilter
from plugins.storage import Storage
from plugins.logger import log


class Consumer:
    def __init__(self,
                 p_storage: Storage,
                 p_monitoring_service: MonitoringService,
                 p_spoofing_zone_filter: SpoofingZoneFilter
                 ):
        self.storage = p_storage
        self.monitoring_service = p_monitoring_service
        self.spoofing_zone_filter = p_spoofing_zone_filter

    def consume_flex_message(self, imei: str, packet_type: str, data: bytes | None, decoded: dict | None):
        """ Обрабатывает декодированное FLEX-сообщение"""
        device_id, new = self.storage.get_device_id_by_imei(imei)
        if new:
            log(f"Новое устройство. IMEI={imei}")
        if packet_type == PACKET_TYPE_PING:
            self.storage.update_last_alive(device_id)
            log(f'{imei}: consumed PING')
        elif packet_type == PACKET_TYPE_HANDSHAKE:
            self.storage.update_last_alive(device_id)
            self.storage.save_message(device_id, 0, packet_type, data, None)
            log(f'{imei}: consumed HANDSHAKE')
        elif packet_type == PACKET_TYPE_APPROVAL:
            self.storage.save_message(device_id, 0, packet_type, data, None)
            log('consumed PACKET_TYPE_APPROVAL')
        elif packet_type == PACKET_TYPE_A or packet_type == PACKET_TYPE_C or packet_type == PACKET_TYPE_T:
            self.storage.update_last_alive(device_id)
            self.debug_message(imei, packet_type, decoded)
            event_id = decoded['2']
            spoofed = False
            if "10" in decoded and "11" in decoded:
                lat = float(decoded.get("10")) / 600000
                lon = float(decoded.get("11")) / 600000
                spoofed =  self.spoofing_zone_filter.point_in_spoofed_zone(lon, lat)
            if spoofed:
                log(f'{imei}: spoofed')
            else:
                self.storage.save_message(device_id, event_id, packet_type, data, decoded)
            moment = decoded.get('3')
            if moment > datetime.now().timestamp() - 300: # Мониторим только события не старше 5 минут
                self.monitoring_service.do_monitoring(device_id, decoded)
        elif packet_type == PACKET_TYPE_ERROR:
            self.storage.save_message(device_id, 0, packet_type, data, decoded)
        else:
            log(f'Unknown packet type: {packet_type}')

    @staticmethod
    def debug_message(device_id: str, packet_type: str, message: dict):
        """ Выводит отдельные поля сообщения в консоль """
        # f = []
        # for i in self.storage.get_param_list('fields_to_show'):
        #     if i in message:
        #         f.append(message[i])
        #     else:
        #         f.append('~')
        # formatted_line = '\t'.join(str(x) for x in f)
        # log(f"{packet_type} {device_id} {formatted_line}")
        log(f"{packet_type} {device_id} {message}")
