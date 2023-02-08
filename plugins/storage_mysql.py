# Плагин. Хранилище устройств в БД MariaDb(Mysql)
from plugins.db_mysql import Db

class Storage(Db):
    def __init__(self, config: dict):
        Db.__init__(self, config['database'])
        self.config = config
        devices_count = self.get_value("SELECT count(1) FROM device")

    def get_device_id_by_imei(self, imei: str) -> tuple:
        device = self.get_value('SELECT id FROM device WHERE imei = %s', [imei])
        if device is not None:
            return device, False
        device_id = self.insert('INSERT INTO device (imei) VALUES (%s)', [imei])
        return device_id, True

    def get_parameter_description(self, parameter_id: int):
        return self.get_value("SELECT description FROM parameter WHERE id = %s", [parameter_id])

    def update_last_alive(self, device_id: int):
        self.execute("UPDATE device SET last_alive = NOW() WHERE id = %s", [device_id])

    def save_message(self, device_id: int, event_id: int, datetime: str,
                     message_type: str, data:bytes | None, decoded: str | None):
        self.insert('INSERT INTO message (device_id, event_id, `datetime`, message_type, data, decoded)'
                    ' VALUES (%s, %s, %s, %s, %s, %s)',
                    [device_id, event_id, datetime, message_type, data, decoded])

    # Возвращает набор параметров для мониторинга данного устройства
    def get_device_monitoring(self, device_id:int) -> dict:
        return self.get_data('SELECT * FROM monitoring WHERE device_id=%s', [device_id])
