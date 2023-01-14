from datetime import datetime
from telegram import Sender
from config import config
from plugins.db_mysql import Db

db = Db(config['database'])
sender = Sender(config['telegram'])


def get_parameter_description(id: int):
    return db.get_value("SELECT description FROM parameter WHERE id = %s", [id])


device_id = 1
decoded = {'21': 3333, # Напряжение на аналоговом входе 1 (Ain1)
           '45': -12  # Температура с цифрового датчика 1 (в градусах Цельсия)
           }
params = db.get_data("SELECT id, parameter_id, event_id, min_value, max_value, `datetime`, timeout, `alert`"
                     " FROM monitoring WHERE device_id = %s", [device_id])
now = datetime.now()
for p in params:
    parameter_id = str(p['parameter_id'])
    if parameter_id not in decoded:
        # Параметра нет в поступившем сообщении
        if 'timeout' in p and p['timeout'] is not None:
            timeout = int(p['timeout'])
        else:
            timeout = config['default_timeout']
        # Проверяем - давно ли появлялся такой параметр
        if 'datetime' in p:
            last_data = p['datetime']
            interval = round((now - last_data).total_seconds())
            if interval > timeout:
                parameter_description = get_parameter_description(parameter_id)
                sender.send_message(device_id,
                                    config['telegram']['chat_id'],
                                    f"Параметр '{parameter_description}' не поступал уже более {interval} с.")
    else:
        value = decoded[parameter_id]
        if value < p['min_value']:
            parameter_description = get_parameter_description(parameter_id)
            sender.send_message(device_id,
                                config['telegram']['chat_id'],
                                f"Значение параметра '{parameter_description}' ({value})"
                                f" меньше допустимого {p['min_value']}")
        elif value > p['max_value']:
            parameter_description = get_parameter_description(parameter_id)
            sender.send_message(device_id,
                                config['telegram']['chat_id'],
                                f"Значение параметра '{parameter_description}' ({value})"
                                f" больше допустимого {p['max_value']}")
            db.execute("UPDATE monitoring SET `datetime`=NOW(), current_value = %s"
                       " WHERE device_id = %s AND parameter_id = %s",
                       [value, device_id, parameter_id])