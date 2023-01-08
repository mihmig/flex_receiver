NTCB_HEADER = b'@NTC'
HANDSHAKE_HEADER = b'*>S:'
FLEX_HEADER = b'*>FLEX'
FLEX_PROTOCOL_CODE = b'\xB0'
FLEX_PROTOCOL_VERSION_1 = b'\x0A'
FLEX_STRUCT_VERSION_1 = b'\x0A'
FLEX_DATASIZE_V1 = b'\x45' # 69 бит (округлённо 9 байт)
# Подтверждение handshake
HANDSHAKE_ANSWER = b'\x40\x4E\x54\x43\x00\x00\x00\x00\x01\x00\x00\x00\x03\x00\x45\x5E\x2A\x3C\x53'
# Подтверждение согласования версий протоколов
VERSION_APPROVAL_ANSWER = b'\x40\x4E\x54\x43\x00\x00\x00\x00\x01\x00\x00\x00\x09\x00\xB1\xA0\x2A\x3C\x46\x4C\x45\x58\xB0\x0A\x0A'
# Ответ на пакет типа С
PACKET_C_ANSWER = b'\x7E\x43\xB9'
PACKET_A_HEADER = b'~A'
PACKET_C_HEADER = b'~C'
PACKET_T_HEADER = b'~T'

# Первый пакет от устройства
PACKET_TYPE_HANDSHAKE = 'HANDSHAKE'
# Пакет согласования версии протокола
PACKET_TYPE_APPROVAL = 'APPROVAL'
# Пустой пакет поддержания канала связи
PACKET_TYPE_PING = 'PING'
# Пакет с телеметрией
PACKET_TYPE_A = 'A'
# Пакет текущего состояния
PACKET_TYPE_C = 'C'
# Пакет внеочередного сообщения
PACKET_TYPE_T = 'T'
# Ошибка разбора пакета
PACKET_TYPE_ERROR = 'ERROR'

LOCAL_PORT = 21626
REMOTE_SERVER = '193.193.165.165'
REMOTE_PORT = 21626
