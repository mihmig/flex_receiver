# Тест контроля параметров на выход за установленные рамки и возвращение в норму
from datetime import datetime

from config import config
from plugins.storage_mysql import Storage
from telegram import Sender

storage = Storage(config)
sender = Sender(config['telegram'])

device_id = 1
decoded = {'21': 2500,  # Напряжение на аналоговом входе 1 (Ain1)
           '45': 1  # Температура с цифрового датчика 1 (в градусах Цельсия)
           }
params = storage.get_data("SELECT id, parameter_id, event_id, min_value, max_value, `datetime`, timeout,"
                          " `alert`, triggered, chat_id"
                          " FROM monitoring WHERE device_id = %s", [device_id])
for p in params:
    id = p['id']
    parameter_id = p.get('parameter_id')
    value = decoded.get(str(parameter_id))
    if value is None:
        continue  # В полученных данных нет данного параметра
    storage.execute("UPDATE monitoring SET `datetime` = %s, current_value = %s WHERE id = %s",
                    [datetime.now(), value, id])
    if value < p['min_value'] and not p['triggered']:
        storage.execute("UPDATE monitoring SET triggered = true WHERE id = %s", [id])
        parameter_description = storage.get_parameter_description(parameter_id)
        sender.send_message(p.get('chat_id') or config['telegram']['chat_id'],
                            f"Значение параметра '{parameter_description}' ({value})"
                            f" меньше допустимого {p['min_value']}")
    elif value > p['max_value'] and not p['triggered']:
        storage.execute("UPDATE monitoring SET triggered = true WHERE id = %s", [id])
        parameter_description = storage.get_parameter_description(parameter_id)
        sender.send_message(p.get('chat_id') or config['telegram']['chat_id'],
                            f"Значение параметра '{parameter_description}' ({value})"
                            f" больше допустимого {p['max_value']}")
    else:
        if p['triggered']:
            parameter_description = storage.get_parameter_description(parameter_id)
            sender.send_message(p.get('chat_id') or config['telegram']['chat_id'],
                                f"Значение параметра '{parameter_description}' ({value})"
                                f" вернулось в норму")
            # Параметр вернулся в норму (TODO предусмотреть гистерезис)
            storage.execute("UPDATE monitoring SET triggered = false WHERE id = %s", [id])
