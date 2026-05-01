# Заголовок протокола
NTCB_HEADER = b'@NTC'
# Ошибка разбора пакета
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
PACKET_TYPE_HANDSHAKE = 'h'
# Пакет согласования версии протокола
PACKET_TYPE_APPROVAL = 'a'
# Пустой пакет поддержания канала связи
PACKET_TYPE_PING = 'p'
# Пакет с телеметрией
PACKET_TYPE_A = 'A'
# Пакет текущего состояния
PACKET_TYPE_C = 'C'
# Пакет внеочередного сообщения
PACKET_TYPE_T = 'T'
PACKET_TYPE_ERROR = 'e'


# Сквозной номер записи в энергонезависимой памяти
FIELD_EEPROM_NUMBER = 1
# Код события
FIELD_EVENT_CODE = 2
# Время события (UNIX TIMESTAMP)
FIELD_EVENT_TIME = 3
# Статус устройства
FIELD_DEVICE_STATUS = 4
# Статус функциональных модулей 1
FIELD_FUNC_MODULES_1_STATUS = 5
# Статус функциональных модулей 2
FIELD_FUNC_MODULES_2_STATUS = 6
# Уровень GSM
FIELD_GSM_LEVEL = 7
# Состояние навигационного датчика GPS/ГЛОНАСС
FIELD_GPS_LEVEL = 8
# Время последних валидных координат
FIELD_LAST_VALID_COORDINATES_TIME = 9
# Последняя валидная широта
FIELD_LAST_VALID_LATITUDE = 10
# Последняя валидная долгота
FIELD_LAST_VALID_LONGITUDE = 11
# Последняя валидная высота
FIELD_LAST_VALID_ALTITUDE = 12
# Скорость
FIELD_SPEED = 13
# Курс
FIELD_DIRECTION = 14
# Текущий пробег
FIELD_CURRENT_MILEAGE = 15
# Последний отрезок пути
FIELD_LAST_LEG = 16
# Общее количество секунд на последнем отрезке пути
FIELD_TOTAL_LAST_LAG_SECONDS = 17
# Количество секунд на последнем отрезке пути, по которым вычислялся пробег (валидная навигация)
FIELD_TOTAL_LAST_VALID_LAG_SECONDS = 18
# Напряжение на основном источнике питания
FIELD_MAIN_SOURCE_VOLTAGE = 19
# Напряжение на резервном источнике питания
FIELD_RESERVED_SOURCE_VOLTAGE = 20
# Напряжение на аналоговом входе 1 (Ain1)
FIELD_ANALOG_INPUT_1_VOLTAGE = 21
# Напряжение на аналоговом входе 2 (Ain2)
FIELD_ANALOG_INPUT_2_VOLTAGE = 22
# Напряжение на аналоговом входе 3 (Ain3)
FIELD_ANALOG_INPUT_3_VOLTAGE = 23
# Напряжение на аналоговом входе 4 (Ain4)
FIELD_ANALOG_INPUT_4_VOLTAGE = 24
# Напряжение на аналоговом входе 5 (Ain5)
FIELD_ANALOG_INPUT_5_VOLTAGE = 25
# Напряжение на аналоговом входе 6 (Ain6)
FIELD_ANALOG_INPUT_6_VOLTAGE = 26
# Напряжение на аналоговом входе 7 (Ain7)
FIELD_ANALOG_INPUT_7_VOLTAGE = 27
# Напряжение на аналоговом входе 8 (Ain8)
FIELD_ANALOG_INPUT_8_VOLTAGE = 28
# Текущие показания дискретных датчиков 1
FIELD_DISCRETE_SENSOR_1 = 29
# Текущие показания дискретных датчиков 2
FIELD_DISCRETE_SENSOR_2 = 30
# Текущее состояние выходов 1
FIELD_OUTPUT_STATE_1 = 31
# Текущее состояние выходов 2
FIELD_OUTPUT_STATE_2 = 32
# Показания счетчика импульсов 1
FIELD_COUNTER_1 = 33
# Показания счетчика импульсов 2
FIELD_COUNTER_2 = 34
# Частота на аналогово-частотном датчике уровня топлива 1
FIELD_AFF_SENSOR_1 = 35
# Частота на аналогово-частотном датчике уровня топлива 2
FIELD_AFF_SENSOR_2 = 36
# Моточасы, подсчитанные во время срабатывания датчика работы генератора
FIELD_MOTO_HOURS = 37
# Уровень топлива, измеренный датчиком уровня топлива 1 RS-485
FIELD_FUEL_LEVEL_1 = 38
# Уровень топлива, измеренный датчиком уровня топлива 2 RS-485
FIELD_FUEL_LEVEL_2 = 39
# Уровень топлива, измеренный датчиком уровня топлива 3 RS-485
FIELD_FUEL_LEVEL_3 = 40
# Уровень топлива, измеренный датчиком уровня топлива 4 RS-485
FIELD_FUEL_LEVEL_4 = 41
# Уровень топлива, измеренный датчиком уровня топлива 5 RS-485
FIELD_FUEL_LEVEL_5 = 42
# Уровень топлива, измеренный датчиком уровня топлива 6 RS-485
FIELD_FUEL_LEVEL_6 = 43
# Нет описания
FIELD_UNKNOWN = 44
# Температура с цифрового датчика 1 (в градусах Цельсия)
FIELD_DIGITAL_TEMP_SENSOR_1 = 45
# Температура с цифрового датчика 2 (в градусах Цельсия)
FIELD_DIGITAL_TEMP_SENSOR_2 = 46
# Температура с цифрового датчика 3 (в градусах Цельсия)
FIELD_DIGITAL_TEMP_SENSOR_3 = 47
# Температура с цифрового датчика 4 (в градусах Цельсия)
FIELD_DIGITAL_TEMP_SENSOR_4 = 48
# Температура с цифрового датчика 5 (в градусах Цельсия)
FIELD_DIGITAL_TEMP_SENSOR_5 = 49
# Температура с цифрового датчика 6 (в градусах Цельсия)
FIELD_DIGITAL_TEMP_SENSOR_6 = 50
# Температура с цифрового датчика 7 (в градусах Цельсия)
FIELD_DIGITAL_TEMP_SENSOR_7 = 51
# Температура с цифрового датчика 8 (в градусах Цельсия)
FIELD_DIGITAL_TEMP_SENSOR_8 = 52
# CAN Уровень топлива в баке
FIELD_CAN_FUEL_LEVEL = 53
# CAN Полный расход топлива
FIELD_CAN_FULL_FUEL_CONSUMPTION = 54
# CAN Обороты двигателя
FIELD_CAN_ENGINE_SPEED = 55
# CAN Температура охлаждающей жидкости (двигателя)
FIELD_CAN_ENGINE_COOLANT_TEMP = 56
# CAN Полный пробег ТС
FIELD_CAN_FULL_VEHICLE_MILEAGE = 57
# CAN Нагрузка на ось 1
FIELD_CAN_AXLE_LOAD_1 = 58
# CAN Нагрузка на ось 2
FIELD_CAN_AXLE_LOAD_2 = 59
# CAN Нагрузка на ось 3
FIELD_CAN_AXLE_LOAD_3 = 60
# CAN Нагрузка на ось 4
FIELD_CAN_AXLE_LOAD_4 = 61
# CAN Нагрузка на ось 5
FIELD_CAN_AXLE_LOAD_5 = 62
# CAN Положение педали газа
FIELD_GAS_PEDAL_POSITION = 63
# CAN Положение педали тормоза
FIELD_CAN_BREAK_PEDAL_POSITION = 64
# CAN Нагрузка на двигатель
FIELD_CAN_ENGINE_LOAD = 65
# CAN Уровень жидкости в дизельном фильтре выхлопных газов
FIELD_CAN_LIQUID_LEVEL_DIESEL_EXHAUST_FILTER = 66
# CAN Полное время работы двигателя
FIELD_CAN_FULL_ENGINE_OPERATING_TIME = 67
# CAN Расстояние до ТО
FIELD_CAN_DISTANCE_TO_INSPECTION = 68
# CAN Скорость ТС
FIELD_CAN_VEHICLE_SPEED = 69


flex_fields = [
    {
        'num': FIELD_EEPROM_NUMBER,
        'byte': 0,
        'bit': 0b1000_0000,
        'size': 4,
        'description': 'Сквозной номер записи в энергонезависимой памяти'
    },
    {
        'num': FIELD_EVENT_CODE,
        'byte': 0,
        'bit': 0b0100_0000,
        'size': 2,
        'description': 'Код события'
    },
    {
        'num': FIELD_EVENT_TIME,
        'byte': 0,
        'bit': 0b0010_0000,
        'size': 4,
        'description': 'Время события'
    },
    {
        'num': FIELD_DEVICE_STATUS,
        'byte': 0,
        'bit': 0b0001_0000,
        'size': 1,
        'description': 'Статус устройства'
    },
    {
        'num': FIELD_FUNC_MODULES_1_STATUS,
        'byte': 0,
        'bit': 0b0000_1000,
        'size': 1,
        'description': 'Статус функциональных модулей 1'
    },
    {
        'num': FIELD_FUNC_MODULES_2_STATUS,
        'byte': 0,
        'bit': 0b0000_0100,
        'size': 1,
        'description': 'Статус функциональных модулей 2'
    },
    {
        'num': FIELD_GSM_LEVEL,
        'byte': 0,
        'bit': 0b0000_0010,
        'size': 1,
        'description': 'Уровень GSM'
    },
    {
        'num': FIELD_GPS_LEVEL,
        'byte': 0,
        'bit': 0b0000_0001,
        'size': 1,
        'description': 'Состояние навигационного датчика GPS/ГЛОНАСС'
    },
    {
        'num': FIELD_LAST_VALID_COORDINATES_TIME,
        'byte': 1,
        'bit': 0b1000_0000,
        'size': 4,
        'description': 'Время последних валидных координат'
    },
    {
        'num': FIELD_LAST_VALID_LATITUDE,
        'byte': 1,
        'bit': 0b0100_0000,
        'size': 4,
        'description': 'Последняя валидная широта'
    },
    {
        'num': FIELD_LAST_VALID_LONGITUDE,
        'byte': 1,
        'bit': 0b0010_0000,
        'size': 4,
        'description': 'Последняя валидная долгота'
    },
    {
        'num': FIELD_LAST_VALID_ALTITUDE,
        'byte': 1,
        'bit': 0b0001_0000,
        'size': 4,
        'description': 'Последняя валидная высота'
    },
    {
        'num': FIELD_SPEED,
        'byte': 1,
        'bit': 0b0000_1000,
        'size': 4,
        'description': 'Скорость'
    },
    {
        'num': FIELD_DIRECTION,
        'byte': 1,
        'bit': 0b0000_0100,
        'size': 2,
        'description': 'Курс'
    },
    {
        'num': FIELD_CURRENT_MILEAGE,
        'byte': 1,
        'bit': 0b0000_0010,
        'size': 4,
        'description': 'Текущий пробег'
    },
    {
        'num': FIELD_LAST_LEG,
        'byte': 1,
        'bit': 0b0000_0001,
        'size': 4,
        'description': 'Последний отрезок пути'
    },
    {
        'num': FIELD_TOTAL_LAST_LAG_SECONDS,
        'byte': 2,
        'bit': 0b1000_0000,
        'size': 2,
        'description': 'Общее количество секунд на последнем отрезке пути'
    },
    {
        'num': FIELD_TOTAL_LAST_VALID_LAG_SECONDS,
        'byte': 2,
        'bit': 0b0100_0000,
        'size': 2,
        'description': 'Количество секунд на последнем отрезке пути, по которым вычислялся пробег (валидная навигация)'
    },
    {
        'num': FIELD_MAIN_SOURCE_VOLTAGE,
        'byte': 2,
        'bit': 0b0010_0000,
        'size': 2,
        'description': 'Напряжение на основном источнике питания'
    },
    {
        'num': FIELD_RESERVED_SOURCE_VOLTAGE,
        'byte': 2,
        'bit': 0b0001_0000,
        'size': 2,
        'description': 'Напряжение на резервном источнике питания'
    },
    {
        'num': FIELD_ANALOG_INPUT_1_VOLTAGE,
        'byte': 2,
        'bit': 0b0000_1000,
        'size': 2,
        'description': 'Напряжение на аналоговом входе 1 (Ain1)'
    },
    {
        'num': FIELD_ANALOG_INPUT_2_VOLTAGE,
        'byte': 2,
        'bit': 0b0000_0100,
        'size': 2,
        'description': 'Напряжение на аналоговом входе 2 (Ain2)'
    },
    {
        'num': FIELD_ANALOG_INPUT_3_VOLTAGE,
        'byte': 2,
        'bit': 0b0000_0010,
        'size': 2,
        'description': 'Напряжение на аналоговом входе 3 (Ain3)'
    },
    {
        'num': FIELD_ANALOG_INPUT_4_VOLTAGE,
        'byte': 2,
        'bit': 0b0000_0001,
        'size': 2,
        'description': 'Напряжение на аналоговом входе 4 (Ain4)'
    },
    {
        'num': FIELD_ANALOG_INPUT_5_VOLTAGE,
        'byte': 3,
        'bit': 0b1000_0000,
        'size': 2,
        'description': 'Напряжение на аналоговом входе 5 (Ain5)'
    },
    {
        'num': FIELD_ANALOG_INPUT_6_VOLTAGE,
        'byte': 3,
        'bit': 0b0100_0000,
        'size': 2,
        'description': 'Напряжение на аналоговом входе 6 (Ain6)'
    },
    {
        'num': FIELD_ANALOG_INPUT_7_VOLTAGE,
        'byte': 3,
        'bit': 0b0010_0000,
        'size': 2,
        'description': 'Напряжение на аналоговом входе 7 (Ain7)'
    },
    {
        'num': FIELD_ANALOG_INPUT_8_VOLTAGE,
        'byte': 3,
        'bit': 0b0001_0000,
        'size': 2,
        'description': 'Напряжение на аналоговом входе 8 (Ain8)'
    },
    {
        'num': FIELD_DISCRETE_SENSOR_1,
        'byte': 3,
        'bit': 0b0000_1000,
        'size': 1,
        'description': 'Текущие показания дискретных датчиков 1'
    },
    {
        'num': FIELD_DISCRETE_SENSOR_2,
        'byte': 3,
        'bit': 0b0000_0100,
        'size': 1,
        'description': 'Текущие показания дискретных датчиков 2'
    },
    {
        'num': FIELD_OUTPUT_STATE_1,
        'byte': 3,
        'bit': 0b0000_0010,
        'size': 1,
        'description': 'Текущее состояние выходов 1'
    },
    {
        'num': FIELD_OUTPUT_STATE_2,
        'byte': 3,
        'bit': 0b0000_0001,
        'size': 1,
        'description': 'Текущее состояние выходов 2'
    },
    {
        'num': FIELD_COUNTER_1,
        'byte': 4,
        'bit': 0b1000_0000,
        'size': 4,
        'description': 'Показания счетчика импульсов 1'
    },
    {
        'num': FIELD_COUNTER_2,
        'byte': 4,
        'bit': 0b0100_0000,
        'size': 4,
        'description': 'Показания счетчика импульсов 2'
    },
    {
        'num': FIELD_AFF_SENSOR_1,
        'byte': 4,
        'bit': 0b0010_0000,
        'size': 2,
        'description': 'Частота на аналогово-частотном датчике уровня топлива 1'
    },
    {
        'num': FIELD_AFF_SENSOR_2,
        'byte': 4,
        'bit': 0b0001_0000,
        'size': 2,
        'description': 'Частота на аналогово-частотном датчике уровня топлива 2'
    },
    {
        'num': FIELD_MOTO_HOURS,
        'byte': 4,
        'bit': 0b0000_1000,
        'size': 4,
        'description': 'Моточасы, подсчитанные во время срабатывания датчика работы генератора'
    },
    {
        'num': FIELD_FUEL_LEVEL_1,
        'byte': 4,
        'bit': 0b0000_0100,
        'size': 2,
        'description': 'Уровень топлива, измеренный датчиком уровня топлива 1 RS-485'
    },
    {
        'num': FIELD_FUEL_LEVEL_2,
        'byte': 4,
        'bit': 0b0000_0010,
        'size': 2,
        'description': 'Уровень топлива, измеренный датчиком уровня топлива 2 RS-485'
    },
    {
        'num': FIELD_FUEL_LEVEL_3,
        'byte': 4,
        'bit': 0b0000_0001,
        'size': 2,
        'description': 'Уровень топлива, измеренный датчиком уровня топлива 3 RS-485'
    },
    {
        'num': FIELD_FUEL_LEVEL_4,
        'byte': 5,
        'bit': 0b1000_0000,
        'size': 2,
        'description': 'Уровень топлива, измеренный датчиком уровня топлива 4 RS-485'
    },
    {
        'num': FIELD_FUEL_LEVEL_5,
        'byte': 5,
        'bit': 0b0100_0000,
        'size': 2,
        'description': 'Уровень топлива, измеренный датчиком уровня топлива 5 RS-485'
    },
    {
        'num': FIELD_FUEL_LEVEL_6,
        'byte': 5,
        'bit': 0b0010_0000,
        'size': 2,
        'description': 'Уровень топлива, измеренный датчиком уровня топлива 6 RS-485'
    },
    {
        'num': FIELD_UNKNOWN,
        'byte': 5,
        'bit': 0b0001_0000,
        'size': 2,
        'description': ''
    },
    {
        'num': FIELD_DIGITAL_TEMP_SENSOR_1,
        'byte': 5,
        'bit': 0b0000_1000,
        'size': 1,
        'description': 'Температура с цифрового датчика 1 (в градусах Цельсия)'
    },
    {
        'num': FIELD_DIGITAL_TEMP_SENSOR_2,
        'byte': 5,
        'bit': 0b0000_0100,
        'size': 1,
        'description': 'Температура с цифрового датчика 2 (в градусах Цельсия)'
    },
    {
        'num': FIELD_DIGITAL_TEMP_SENSOR_3,
        'byte': 5,
        'bit': 0b0000_0010,
        'size': 1,
        'description': 'Температура с цифрового датчика 3 (в градусах Цельсия)'
    },
    {
        'num': FIELD_DIGITAL_TEMP_SENSOR_4,
        'byte': 5,
        'bit': 0b0000_0001,
        'size': 1,
        'description': 'Температура с цифрового датчика 4 (в градусах Цельсия)'
    },
    {
        'num': FIELD_DIGITAL_TEMP_SENSOR_5,
        'byte': 6,
        'bit': 0b1000_0000,
        'size': 1,
        'description': 'Температура с цифрового датчика 5 (в градусах Цельсия)'
    },
    {
        'num': FIELD_DIGITAL_TEMP_SENSOR_6,
        'byte': 6,
        'bit': 0b0100_0000,
        'size': 1,
        'description': 'Температура с цифрового датчика 6 (в градусах Цельсия)'
    },
    {
        'num': FIELD_DIGITAL_TEMP_SENSOR_7,
        'byte': 6,
        'bit': 0b0010_0000,
        'size': 1,
        'description': 'Температура с цифрового датчика 7 (в градусах Цельсия)'
    },
    {
        'num': FIELD_DIGITAL_TEMP_SENSOR_8,
        'byte': 6,
        'bit': 0b0001_0000,
        'size': 1,
        'description': 'Температура с цифрового датчика 8 (в градусах Цельсия)'
    },
    {
        'num': FIELD_CAN_FUEL_LEVEL,
        'byte': 6,
        'bit': 0b0000_1000,
        'size': 2,
        'description': 'CAN Уровень топлива в баке'
    },
    {
        'num': FIELD_CAN_FULL_FUEL_CONSUMPTION,
        'byte': 6,
        'bit': 0b0000_0100,
        'size': 4,
        'description': 'CAN Полный расход топлив'
    },
    {
        'num': FIELD_CAN_ENGINE_SPEED,
        'byte': 6,
        'bit': 0b0000_0010,
        'size': 2,
        'description': 'CAN Обороты двигателя'
    },
    {
        'num': FIELD_CAN_ENGINE_COOLANT_TEMP,
        'byte': 6,
        'bit': 0b0000_0001,
        'size': 1,
        'description': 'CAN Температура охлаждающей жидкости (двигателя)'
    },
    {
        'num': FIELD_CAN_FULL_VEHICLE_MILEAGE,
        'byte': 7,
        'bit': 0b1000_0000,
        'size': 4,
        'description': 'CAN Полный пробег ТС'
    },
    {
        'num': FIELD_CAN_AXLE_LOAD_1,
        'byte': 7,
        'bit': 0b0100_0000,
        'size': 2,
        'description': 'CAN Нагрузка на ось 1'
    },
    {
        'num': FIELD_CAN_AXLE_LOAD_2,
        'byte': 7,
        'bit': 0b0010_0000,
        'size': 2,
        'description': 'CAN Нагрузка на ось 2'
    },
    {
        'num': FIELD_CAN_AXLE_LOAD_3,
        'byte': 7,
        'bit': 0b0001_0000,
        'size': 2,
        'description': 'CAN Нагрузка на ось 3'
    },
    {
        'num': FIELD_CAN_AXLE_LOAD_4,
        'byte': 7,
        'bit': 0b0000_1000,
        'size': 2,
        'description': 'CAN Нагрузка на ось 4'
    },
    {
        'num': FIELD_CAN_AXLE_LOAD_5,
        'byte': 7,
        'bit': 0b0000_0100,
        'size': 2,
        'description': 'CAN Нагрузка на ось 5'
    },
    {
        'num': FIELD_GAS_PEDAL_POSITION,
        'byte': 7,
        'bit': 0b0000_0010,
        'size': 1,
        'description': 'CAN Положение педали газа'
    },
    {
        'num': FIELD_CAN_BREAK_PEDAL_POSITION,
        'byte': 7,
        'bit': 0b0000_0001,
        'size': 1,
        'description': 'CAN Положение педали тормоза'
    },
    {
        'num': FIELD_CAN_ENGINE_LOAD,
        'byte': 8,
        'bit': 0b1000_0000,
        'size': 1,
        'description': 'CAN Нагрузка на двигатель'
    },
    {
        'num': FIELD_CAN_LIQUID_LEVEL_DIESEL_EXHAUST_FILTER,
        'byte': 8,
        'bit': 0b0100_0000,
        'size': 2,
        'description': 'CAN Уровень жидкости в дизельном фильтре выхлопных газов'
    },
    {
        'num': FIELD_CAN_FULL_ENGINE_OPERATING_TIME,
        'byte': 8,
        'bit': 0b0010_0000,
        'size': 4,
        'description': 'CAN Полное время работы двигателя'
    },
    {
        'num': FIELD_CAN_DISTANCE_TO_INSPECTION,
        'byte': 8,
        'bit': 0b0001_0000,
        'size': 2,
        'description': 'CAN Расстояние до ТО'
    },
    {
        'num': FIELD_CAN_VEHICLE_SPEED,
        'byte': 8,
        'bit': 0b0000_1000,
        'size': 1,
        'description': 'CAN Скорость ТС'
    }
]

