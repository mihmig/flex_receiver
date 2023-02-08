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
final_message = "Текущее состояние системы охлаждения аквариума:\n"

device_id = 4


def get_param_info(parameter_id: int, parameter_name: str) -> str:
    p = storage.get_line("SELECT id, parameter_id, event_id, current_value, min_value, max_value,"
                         " below_min_message, above_max_message, "
                         " `alert`, triggered, chat_id"
                         " FROM monitoring WHERE device_id = %s AND parameter_id = %s", [device_id, parameter_id])

    if p['current_value'] < p['min_value'] or p['current_value'] > p['max_value']:
        message = "🔴 "
    else:
        message = "🟢 "
    message += f"{parameter_name}: {round(p['current_value'])} °C\n"
    return message


final_message += get_param_info(49, "Температура воды подача")
final_message += get_param_info(51, "Температура воздуха")
sender.send_message(chat_id, final_message)
