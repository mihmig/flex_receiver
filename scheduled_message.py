# Отправка текущего состояния.
# в 10 и в 20 часов регулярно выплевывать:
#
# Текущее состояние системы охлаждения аквариума:
# 🟢 Температура воды подача: 9 °C
# 🔴 Температура воздуха 18 °C
from datetime import datetime
from config import config
from plugins.storage_mysql import Storage
from telegram import Sender

sender = Sender(config['telegram'])
storage = Storage(config)

chat_id = -1001882219961
# chat_id = 47254369
final_message = "Текущее состояние системы охлаждения аквариума:\n"

device_id = 4


def get_param_info(parameter_id: int, messages: dict) -> str:
    p = storage.get_line("SELECT id, parameter_id, event_id, current_value, min_value, max_value,"
                         " below_min_message, above_max_message, "
                         " `alert`, triggered, chat_id"
                         " FROM monitoring WHERE device_id = %s AND parameter_id = %s", [device_id, parameter_id])

    value_str = str(round(p['current_value']))
    if p['current_value'] < p['min_value']:
        return messages['below'].replace('%VALUE%', value_str)
    elif p['current_value'] > p['max_value']:
        return messages['above'].replace('%VALUE%', value_str)
    else:
        return messages['normal'].replace('%VALUE%', value_str)


final_message += get_param_info(49, {'normal': '🟢 Температура воды (подача): %VALUE% °C',
                                     'below': '🔴 Температура воды (подача) : %VALUE% °C',
                                     'above': '🔴 Температура воды (подача) : %VALUE% °C',
                                     }) + '\n'
final_message += get_param_info(51, {'normal': '🟢 Температура воздуха: %VALUE% °C',
                                     'below': '🔴 Температура воздуха: %VALUE% °C',
                                     'above': '🔴 Температура воздуха: %VALUE% °C',
                                     }) + '\n'
final_message += get_param_info(51, {'normal': '🟢 Внешнее питание терминала в норме',
                                     'below': '🔴 Внешнее питание терминала ниже нормы',
                                     'above': '🔴 Внешнее питание терминала выше нормы',
                                     }) + '\n'
sender.send_message(chat_id, final_message)
