# Обработчик входящих пакетов от устройств, работающих по протоколу FLEX
# https://wiki.navtelecom.ru/ru/home/developers/flex_examples
from functools import reduce

# Декодирует входящие данные
# 1. Определяет тип пакета
# 2. Декодирует данные (если таковые есть в пакете)
# data - двоичные данные.
# Возвращает словарь:
# а) Тип разобранного пакета ('error' в случае ошибки)
# б) Данные, которые нужно вернуть устройству (для пакетов, требующих ответа)
# в) Список декодированных FLEX-структур данных (если таковые есть в пакете)
# г) Сообщение о разборе пакета (ошибка или информационное)
from plugins.flex_decoder import decode_field
from plugins.flex_constants import *

digital_sensor_list = [45, 46, 47, 48, 49, 50, 51, 52]


def decode_packet(data):
    packet_header = data[0:2]
    if packet_header == PACKET_A_HEADER:
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
    elif packet_header == PACKET_C_HEADER:
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
    elif packet_header == PACKET_T_HEADER:
        # Внеочередное сообщение ~T<eventindex><x><crc8> (ответ: ~T<eventindex><crc8>)
        eventindex = data[2:6]
        return {
            'packet_type': PACKET_TYPE_T,
            'eventindex': eventindex,
            'payload': data[6:-1],
            'message': f'Packet T, length: {len(data)} bytes. Event index: {eventindex}'
        }
    elif packet_header == PACKET_X_HEADER:
        # Внеочередное сообщение (FLEX 2.0) (~X<eventindex><x><crc8> (ответ: ~X<eventindex><crc8>)
        eventindex = data[2:6]
        return {
            'packet_type': PACKET_TYPE_T,
            'eventindex': eventindex,
            'payload': data[6:-1],
            'message': f'Packet T, length: {len(data)} bytes. Event index: {eventindex}'
        }
    elif packet_header == PACKET_E_HEADER:
        # Для хранения и передачи некоторых редко изменяющихся данных используются дополнительные пакеты
        # и телеметрическая запись, введённые в расширении протокола FLEX 2.0.
        # Данные пакеты заменяют стандартные телеметрические.
        records_count = int.from_bytes(data[2:3], "little", signed=False)
        return {
            'packet_type': PACKET_TYPE_E,
            'records_count': records_count,
            'payload': data[3:-1],
            'message': f'Packet E, length: {len(data)} bytes. Records count: {records_count}'
        }

    elif len(data) > 20 and data[0:4] == NTCB_HEADER and data[16:20] == HANDSHAKE_HEADER:
        imei = data[20:35].decode('ascii')
        return {
            'packet_type': PACKET_TYPE_HANDSHAKE,
            'imei': imei,
            'message': f'HANDSHAKE packet, client IMEI: {imei}'
        }
    elif len(data) > 20 and data[0:4] == NTCB_HEADER and data[16:22] == FLEX_HEADER:
        return get_protocol_version_and_fields(data)
    else:
        return {
            'packet_type': PACKET_TYPE_ERROR,
            'message': f"unknown data packet. length: {len(data)}, first 10 bytes: {data[0:10].hex(' ')}"
        }

def get_protocol_version_and_fields(data) -> dict:
    if data[22:23] != FLEX_PROTOCOL_CODE:
        return {
            'packet_type': PACKET_TYPE_ERROR,
            'message': f'unknown protocol code: {data[22:23]} (need \\xB0)'
        }

    protocol_version_code = data[23:24]
    if protocol_version_code not in [FLEX_PROTOCOL_VERSION_1, FLEX_PROTOCOL_VERSION_2, FLEX_PROTOCOL_VERSION_3]:
        return {
            'packet_type': PACKET_TYPE_ERROR,
            'message': f'unknown protocol version code : {protocol_version_code.hex()}, need (0A,14 or 1E)'
        }
    
    struct_version_code = data[24:25]
    if struct_version_code not in [FLEX_STRUCT_VERSION_1, FLEX_STRUCT_VERSION_2, FLEX_STRUCT_VERSION_3]:
        return {
            'packet_type': PACKET_TYPE_ERROR,
            'message': f'unknown struct version code : {protocol_version_code.hex()}, need (0A,14 or 1E)'
        }
    fields_count = ord(data[25:26]) # 69, 122 или 255 (в зависимости от версии протокола FLEX 1.0,2.0 или 3.0)
    fields = decode_fields(data[26:], fields_count)
    # Количество байт, необходимых для передачи данных только указанных полей структуры FLEX
    structure_length = reduce(lambda a, b: a + b['size'], fields, 0)

    return {
        'packet_type': PACKET_TYPE_APPROVAL,
        'protocol_version_code': protocol_version_code,
        'struct_version_code': struct_version_code,
        'fields': fields,
        'fields_count': fields_count,
        'structure_length': structure_length,
        'message': f'VERSION_APPROVAL packet, structure length: {len(fields)}'
    }


# Декодирует пакет согласования структуры данных FLEX
# (какие параметры будут передаваться)
def decode_fields(data: bytes, p_count: int) -> list[dict]:
    fields = []
    for f in flex_fields[:p_count]:
        if data[f['byte']] & f['bit']:
            fields.append(f)
    return fields

# Декодирует FLEX-пакет с данными
# fields - список ожидаемых полей пакета
# data - двоичные данные FLEX-структуры
# return - Словарь с декодированными данными {'1':'123', '2':'456'}
def decode_flex_message(fields: list, data: bytes) -> dict:
    result = {}
    pointer = 0
    for f in fields:
        value_data = data[pointer:pointer + f['size']]
        # Специальная проверка на показания цифровых датчиков
        # (если с прибора приходит -128 - значит датчик не подключен)
        if f['num'] in digital_sensor_list:
            value = decode_field(f, value_data)
            if value != -128:
                result[str(f['num'])] = value
        else:
            result[str(f['num'])] = decode_field(f, value_data)

        pointer += f['size']
    return result
