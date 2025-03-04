# Обработчик входящих пакетов от устройств
from functools import reduce

from constants import *
# Декодирует входящие данные
# 1. Определяет тип пакета
# 2. Декодирует данные (если таковые есть в пакете)
# data - двоичные данные.
# Возвращает словарь:
# а) Тип разобранного пакета ('error' в случае ошибки)
# б) Данные, которые нужно вернуть устройству (для пакетов, требующих ответа)
# в) Список декодированных FLEX-структур данных (если таковые есть в пакете)
# г) Сообщение о разборе пакета (ошибка или информационное)
from fields import flex_fields, decode_field

digital_sensor_list = [45, 46, 47, 48, 49, 50, 51, 52]

def decode_packet(data):
    if data[0:2] == PACKET_A_HEADER:
        # Массив телеметрических сообщений.
        # Пакет содержит определённое число записей из «чёрного ящика».
        # Размер пакета не превышает 1,3 Кб (не считая заголовка).
        # Допускаются пакеты с одной записью.
        records_count = int.from_bytes(data[2:3], "little", signed=False)
        return {
            'packet_type': PACKET_TYPE_A,
            'records_count': records_count,
            'payload': data[3:-1],
            'message': f'Packet A, length: {len(data)} bytes. Records count: {records_count}'
        }
    elif data[0:2] == PACKET_C_HEADER:
        # Данные о текущем состоянии.
        # Пакет может как добавляться к передаваемым массивам (~A) в качестве последней записи, так и
        # содержаться в отдельном пакете (~C). Текущее состояние имеет нулевой индекс записи и код события 0xFF00.
        return {
            'packet_type': PACKET_TYPE_C,
            'payload': data[2:-1],
            'message': f'Packet C, length: {len(data)} bytes.'
        }
    elif len(data) == 1 and data == b'\x7F':
        # Для поддержания связи (ping) используется пакет, состоящий из одного байта с фиксированным
        # значением 0x7F. Подтверждение со стороны сервера на этот пакет не требуется.
        return {
            'packet_type': PACKET_TYPE_PING,
            'payload': None,
            'message': f'PING packet'
        }
    elif data[0:2] == PACKET_T_HEADER:
        # Внеочередное сообщение ~T<eventindex><x><crc8> (ответ: ~T<eventindex><crc8>)
        eventindex = data[2:6]
        return {
            'packet_type': PACKET_TYPE_T,
            'eventindex': eventindex,
            'payload': data[6:-1],
            'message': f'Packet T, length: {len(data)} bytes. Event index: {eventindex}'
        }
    elif len(data) > 20 and data[0:4] == NTCB_HEADER and data[16:20] == HANDSHAKE_HEADER:
        imei = data[20:35].decode('ascii')
        return {
            'packet_type': PACKET_TYPE_HANDSHAKE,
            'imei': imei,
            'message': f'HANDSHAKE packet, client IMEI: {imei}'
        }
    elif len(data) > 20 and data[0:4] == NTCB_HEADER and data[16:22] == FLEX_HEADER:
        error = None
        if data[22:23] != FLEX_PROTOCOL_CODE:
            error = f'unknown protocol code {data[22:23]}'
        elif data[23:24] != FLEX_PROTOCOL_VERSION_1:
            error = f'unknown protocol version code {data[23:24]}'
        elif data[24:25] != FLEX_STRUCT_VERSION_1:
            error = f'unknown structure version code {data[24:25]}'
        elif data[25:26] != FLEX_DATASIZE_V1:
            error = f'unknown datasize {data[25:26]}'
        if error is not None:
            return {
                'packet_type': PACKET_TYPE_ERROR,
                'message': error
            }
        fields = decode_version_approval(data[26:])
        return {
            'packet_type': PACKET_TYPE_APPROVAL,
            'fields': fields,
            'structure_length': get_structure_length(fields),
            'message': f'VERSION_APPROVAL packet, structure length: {len(fields)}'
        }
    else:
        return {
            'packet_type': PACKET_TYPE_ERROR,
            'message': f"unknown data packet. length: {len(data)}, first 10 bytes: {data[0:10].hex(' ')}"
        }


# Декодирует пакет согласования структуры данных FLEX
# (какие параметры будут передаваться)
def decode_version_approval(data):
    fields = []
    for f in flex_fields:
        if data[f['byte']] & f['bit']:
            fields.append(f)
    return fields


# Определяет количество байт, необходимых для передачи данных только указанных полей структуры FLEX
def get_structure_length(fields: list):
    return reduce(lambda a, b: a + b['size'], fields, 0)


# Декодирует FLEX-пакет с данными
# fields - список ожидаемых полей пакета
# data - двоичные данные FLEX-структуры
# return - Словарь с декодированными данными {'1':'123', '2':'456'}
def decode_flex_message(fields: list, data: str) -> dict:
    result = {}
    pointer = 0
    for f in fields:
        value = data[pointer:pointer + f['size']]
        # Специальная проверка на показания цифровых датчиков
        # (если с прибора приходит -128 - значит датчик не подключен)
        if f['num'] in digital_sensor_list:
            value = decode_field(f, value)
            if value != -128:
                result[str(f['num'])] = value
        else:
            result[str(f['num'])] = decode_field(f, value)

        pointer += f['size']
    return result
