# Отправка текущего состояния.
# в 10 и в 20 часов регулярно выплевывать:
#
# Текущее состояние системы охлаждения аквариума:
# 🟢 Температура воды подача: 9 °C
# 🔴 Температура воздуха 18 °C
from datetime import datetime, timedelta
from config import config
from plugins.storage_mysql import Storage
from telegram import Sender

sender = Sender(config['telegram'])
storage = Storage(config)

chat_id = config['telegram']['chat_id']
final_message = "Текущее состояние системы охлаждения аквариума:\n"

device_id = 4


# Возвращает состояние параметра в человекочитаемом виде
# и необходимость внимания (True - требует внимания, False - норма)
def get_param_state_and_alert(parameter_id: int, messages: dict) -> (str, bool):
    p = storage.get_line("SELECT id, parameter_id, event_id, current_value, min_value, max_value,"
                         " `datetime`, timeout, no_data_message,"
                         " below_min_message, above_max_message, "
                         " `alert`, triggered, chat_id"
                         " FROM monitoring WHERE device_id = %s AND parameter_id = %s", [device_id, parameter_id])

    timeout = 3600 if p['timeout'] is None else p['timeout']
    no_data_message = 'Нет данных длительное время' if p['no_data_message'] is None else p['no_data_message']
    if p['datetime'] is None or p['datetime'] < datetime.now() - timedelta(seconds=timeout):
        return no_data_message, True
    value_str = str(round(p['current_value']))
    if p['current_value'] < p['min_value']:
        return messages['below'].replace('%VALUE%', value_str), True
    elif p['current_value'] > p['max_value']:
        return messages['above'].replace('%VALUE%', value_str), True
    else:
        return messages['normal'].replace('%VALUE%', value_str), False


notification = False

info, alert = get_param_state_and_alert(49, {'normal': '🟢 Температура воды (подача): %VALUE% °C',
                                             'below': '🔴 Температура воды (подача) : %VALUE% °C',
                                             'above': '🔴 Температура воды (подача) : %VALUE% °C',
                                             })
final_message += info + '\n'
if alert:
    notification = True

info, alert = get_param_state_and_alert(51, {'normal': '🟢 Температура воздуха: %VALUE% °C',
                                             'below': '🔴 Температура воздуха: %VALUE% °C',
                                             'above': '🔴 Температура воздуха: %VALUE% °C',
                                             })
final_message += info + '\n'
if alert:
    notification = True

info, alert = get_param_state_and_alert(19, {'normal': '🟢 Внешнее питание терминала в норме',
                                             'below': '🔴 Внешнее питание терминала ниже нормы',
                                             'above': '🔴 Внешнее питание терминала выше нормы',
                                             })
final_message += info + '\n'
if alert:
    notification = True

sender.send_message(chat_id, final_message, not notification)
