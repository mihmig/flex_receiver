# Контроль устройств и их параметров.
from constants import EVENT_TIME_FIELD
from plugins.alert_service import AlertService
from plugins.storage_mysql import Storage


class MonitoringService:
    def __init__(self, storage: Storage, p_alert_service: AlertService):
        self.storage = storage
        self.alert_service = p_alert_service

    def do_monitoring(self, device_id: int, decoded: dict) -> None:
        """ Контроль параметров на выход за установленные рамки и возвращение в норму """
        moment_str = decoded.get(EVENT_TIME_FIELD)
        device = self.storage.get_device(device_id)
        if device is None:
            return
        for param in self.storage.get_params_for_device(device_id):
            _id = param['id']
            parameter_id = param.get('parameter_id')
            value = decoded.get(str(parameter_id))
            if value is None:
                continue  # В полученных данных нет данного параметра
            self.storage.update_parameter(_id, value)

            # Проверки на выход параметра за пределы и возврат в норму
            if value < param['min_value']:
                if not param['triggered']:
                    # Мониторинг уже сработал, повторно уведомления не рассылаем до возврата параметра внорму
                    self.storage.set_triggered(_id)
                    if param.get('alert') and device.get('alert'):
                        if param['below_min_message']:
                            message = param['below_min_message'].replace("%VALUE%", str(value)) \
                                .replace("%MOMENT%", str(moment_str))
                        else:
                            parameter_description = self.storage.get_parameter_description(parameter_id)
                            message = f"Значение параметра '{parameter_description}' " \
                                      f"на {moment_str} ({value}) " \
                                      f"меньше допустимого {param['min_value']}"
                        self.alert_service.send_alert(device, param, message)

            elif value > param['max_value']:
                if not param['triggered']:
                    self.storage.set_triggered(_id)
                    if param.get('alert') and device.get('alert'):
                        if param['above_max_message']:
                            message = param['above_max_message'].replace("%VALUE%", str(value)) \
                                .replace("%MOMENT%", str(moment_str))
                        else:
                            parameter_description = self.storage.get_parameter_description(parameter_id)
                            message = f"Значение параметра '{parameter_description}' " \
                                      f"на {moment_str} ({value}) " \
                                      f"больше допустимого {param['max_value']}"
                        self.alert_service.send_alert(device, param, message)
            else:
                if param['triggered']:
                    # Параметр вернулся в норму (TODO предусмотреть гистерезис)
                    self.storage.reset_triggered(_id)
                    if param.get('alert') and device.get('alert'):
                        if param.get('in_range_message'):
                            message = param['in_range_message'].replace("%VALUE%", str(value)) \
                                .replace("%MOMENT%", str(moment_str))
                        else:
                            parameter_description = self.storage.get_parameter_description(parameter_id)
                            message = f"Значение параметра '{parameter_description}' " \
                                      f"на {moment_str} ({value}) вернулось в норму"
                        self.alert_service.send_alert(device, param, message)
