# Модуль обработки FLEX-пакетов данных
import json
from datetime import datetime
from plugins.flex_constants import PACKET_TYPE_HANDSHAKE, PACKET_TYPE_APPROVAL, PACKET_TYPE_PING, PACKET_TYPE_A, \
    PACKET_TYPE_C, PACKET_TYPE_T, PACKET_TYPE_ERROR
from plugins.monitoring_service import MonitoringService
from plugins.geofences_service import GeofenceService
from plugins.storage import Storage
from plugins.logger import log

# Параметры сообщения, относящиеся к GNSS
GNSS_KEYS = ['9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '70', '71']


class Consumer:
    def __init__(self,
                 p_storage: Storage,
                 p_monitoring_service: MonitoringService,
                 p_spoofing_zone_filter: GeofenceService
                 ):
        self.storage = p_storage
        self.monitoring_service = p_monitoring_service
        self.spoofing_zone_filter = p_spoofing_zone_filter

    def gnss_valid(self, data: dict) -> bool:
        """ Определяет - валидны ли координаты """
        # Невалидная навигация
        if not data.get('8', 0) & 2:
            return False
        # Последние валидные координаты были более 10 секунд назад
        if data.get('3', 100) - data.get('9', 0) > 10:
            return False
        if "10" not in data or "11" not in data:
            return False
        lat = float(data.get("10")) / 600000
        lon = float(data.get("11")) / 600000
        if self.spoofing_zone_filter.point_in_spoofed_zone(lon, lat):
            return False
        return True

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
            # Отключено, не требуется
            # self.storage.save_message(device_id, 0, packet_type, data, None)
            log(f'{imei}: consumed HANDSHAKE')
        elif packet_type == PACKET_TYPE_APPROVAL:
            # Отключено, не требуется
            # self.storage.save_message(device_id, 0, packet_type, data, None)
            log('consumed PACKET_TYPE_APPROVAL')
        elif packet_type == PACKET_TYPE_A or packet_type == PACKET_TYPE_C or packet_type == PACKET_TYPE_T:
            self.storage.update_last_alive(device_id)
            self.debug_message(imei, packet_type, decoded)
            if '9' in decoded and not self.gnss_valid(decoded):  # Если координаты есть - проверяем их валидность
                log(f'{imei}: spoofed/invalid')
                # Удаляем ключи (они всё равно невалидны)
                for key in GNSS_KEYS:
                    decoded.pop(key, None)
                # Пытаемся извлечь примерные координаты по вышкам сотовой связи
            event_id = decoded['2']
            self.storage.save_message(device_id, event_id, packet_type, data, decoded)
            moment = decoded.get('3')
            if moment > datetime.now().timestamp() - 300:  # Мониторим только события не старше 5 минут
                self.monitoring_service.do_monitoring(device_id, decoded)
        elif packet_type == PACKET_TYPE_ERROR:
            self.storage.save_message(device_id, 0, packet_type, data, decoded)
        else:
            log(f'Unknown packet type: {packet_type}')

    @staticmethod
    def debug_message(device_id: str, packet_type: str, message: dict):
        """ Выводит декодированное сообщение в консоль """
        log(f"{packet_type} {device_id} {message}")
