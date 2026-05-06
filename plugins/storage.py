# Плагин. Хранилище устройств в БД MariaDb(Mysql)
import json
from datetime import datetime, timezone
from typing import Any

from plugins.db_mysql import Db


class Storage(Db):
    def __init__(self):
        Db.__init__(self)
        self.device_id_cache = {}
        self.device_cache = {}
        self.system_parameters_cache = self.get_system_parameters()

    def get_device_id_by_imei(self, imei: str) -> tuple:
        if imei in self.device_id_cache:
            device_id = self.device_id_cache[imei]
            return device_id, False
        device_id = self.get_value('SELECT id FROM device WHERE imei = %s', [imei])
        if device_id is not None:
            return device_id, False
        device_id = self.insert('INSERT INTO device (imei) VALUES (%s)', [imei])
        self.device_id_cache[imei] = device_id
        return device_id, True

    def get_device(self, device_id: int) -> dict| None:
        if device_id in self.device_cache:
            return self.device_cache[device_id]
        device = self.get_line('SELECT * FROM device WHERE id = %s', [device_id])
        if device is not None:
            self.device_cache[device_id] = device
        return device

    def get_parameter_description(self, parameter_id: int) -> str:
        """ Возвращает описание параметра. """
        return self.get_value("SELECT description FROM parameter WHERE id = %s", [parameter_id])

    def update_last_alive(self, device_id: int) -> None:
        """ Обновляет время, когда устройство последний раз было онлайн. """
        self.execute("UPDATE device SET last_alive = NOW() WHERE id = %s", [device_id])

    def update_device_state(self, device: dict, state: str) -> None:
        self.execute("UPDATE device SET state = %s WHERE id = %s", [state, device['id']])

    def save_message(self, device_id: int, event_id: int,
                     message_type: str, data: bytes | None, decoded: dict | None):
        moment = datetime.fromtimestamp(decoded.get('3'), tz=timezone.utc) if decoded else None
        self.insert("""INSERT INTO message (device_id, event_id, message_type,
                                            data, decoded, moment)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    [device_id, event_id, message_type,
                     data, json.dumps(decoded) if decoded is not None else None, moment])

    def get_device_monitoring_param(self, device_id: int, parameter_id: int) -> dict:
        """
        Возвращает информацию о контролируемом параметре устройства
        :param device_id: id устройства
        :param parameter_id: id параметра
        :return: словарь с данными
        """
        """  """
        return self.get_line("""
                             SELECT * FROM monitoring 
                             WHERE device_id = %s AND parameter_id = %s
                 """,
                      [device_id, parameter_id])

    def get_system_parameters(self) -> dict:
        """ Возвращает все параметры системы. """
        return self.get_dict('SELECT `key`, `value` FROM settings')

    def get_system_param(self, param_name: str) -> str:
        """ Возвращает конкретный параметр системы. """
        value = self.system_parameters_cache.get(param_name)
        if value is not None:
            return value
        value = self.get_value('SELECT `value` FROM settings WHERE `key` = %s', [param_name])
        if value is not None:
            self.system_parameters_cache[param_name] = value
        return value

    def get_param_list(self, param_name: str) -> list[str]:
        value = self.system_parameters_cache.get(param_name)
        if value is not None:
            return value
        value = self.get_value('SELECT `value` FROM settings WHERE `key` = %s', [param_name])
        if not value:
            return []
        param_list = value.split(',')
        self.system_parameters_cache[param_name] = param_list
        return param_list

    def get_params_for_device(self, device_id: int) -> list[dict]:
        """ Возвращает список контролируемых параметров устройства. """
        return self.get_data("SELECT * FROM monitoring WHERE device_id = %s", [device_id])

    def update_parameter(self, _id: int, value: Any):
        """ Обновляет значение параметра. """
        self.execute("UPDATE monitoring SET `datetime` = %s, current_value = %s WHERE id = %s",
                             [datetime.now(), value, _id])

    def set_triggered(self, _id: int) -> None:
        """ Устанавливаем флаг выхода значение параметра за допустимые пределы """
        self.execute("UPDATE monitoring SET triggered = true WHERE id = %s", [_id])

    def reset_triggered(self, _id: int) -> None:
        """ Устанавливаем флаг выхода значение параметра за допустимые пределы """
        self.execute("UPDATE monitoring SET triggered = false WHERE id = %s", [_id])

    def get_active_geo_zones(self) -> list[dict]:
        """ Возвращает список активных геозон. """
        return self.get_data("SELECT id, name, tags, source_geo, alert, type FROM geo_zone WHERE enabled = true")

    def get_device_messages(self, device_id, start, end):
        return self.get_data("""SELECT id, decoded
                        FROM message 
                        WHERE device_id = %s 
                        AND message_type = 'A'
                        AND decoded IS NOT NULL AND decoded <> 'null'
                        AND moment BETWEEN %s AND %s
                        ORDER BY moment
                      """,
                      [device_id, start, end])

    def upsert_lbs_station(self, station: dict) -> None:
        """
        Создает или обновляет запись о базовой станции.
        """
        self.execute(
            """INSERT INTO lbs (
                   id, num, lat, lon, locType, bsType, bands, valid
               )
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
               ON DUPLICATE KEY UPDATE
                   num = VALUES(num),
                   lat = VALUES(lat),
                   lon = VALUES(lon),
                   locType = VALUES(locType),
                   bsType = VALUES(bsType),
                   bands = VALUES(bands),
                   valid = VALUES(valid),
                   updated = CURRENT_TIMESTAMP
            """,
            [
                station['id'],
                station['num'],
                station['lat'],
                station['lon'],
                station['locType'],
                station['bsType'],
                station.get('bands', ''),
                station.get('valid', True),
            ],
        )

    def upsert_lbs_stations(self, stations: list[dict]) -> int:
        """
        Создает или обновляет список записей о базовых станциях.
        :return: количество обработанных записей
        """
        for station in stations:
            self.upsert_lbs_station(station)
        return len(stations)
    