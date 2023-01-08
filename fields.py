# Описание полей FLEX-структуры и методы для их декодирования
import struct
from datetime import datetime

flex_fields = [
    {
        'num': 1,
        'byte': 0,
        'bit': 0b1000_0000,
        'size': 4,
        'description': 'Сквозной номер записи в энергонезависимой памяти'
    },
    {
        'num': 2,
        'byte': 0,
        'bit': 0b0100_0000,
        'size': 2,
        'description': 'Код события, соответствующий данной записи'
    },
    {
        'num': 3,
        'byte': 0,
        'bit': 0b0010_0000,
        'size': 4,
        'description': 'Время события'
    },
    {
        'num': 4,
        'byte': 0,
        'bit': 0b0001_0000,
        'size': 1,
        'description': 'Статус устройства'
    },
    {
        'num': 5,
        'byte': 0,
        'bit': 0b0000_1000,
        'size': 1,
        'description': 'Статус функциональных модулей 1'
    },
    {
        'num': 6,
        'byte': 0,
        'bit': 0b0000_0100,
        'size': 1,
        'description': 'Статус функциональных модулей 2'
    },
    {
        'num': 7,
        'byte': 0,
        'bit': 0b0000_0010,
        'size': 1,
        'description': 'Уровень GSM'
    },
    {
        'num': 8,
        'byte': 0,
        'bit': 0b0000_0001,
        'size': 1,
        'description': 'Состояние навигационного датчика GPS/ГЛОНАСС'
    },
    {
        'num': 9,
        'byte': 1,
        'bit': 0b1000_0000,
        'size': 4,
        'description': 'Время последних валидных координат'
    },
    {
        'num': 10,
        'byte': 1,
        'bit': 0b0100_0000,
        'size': 4,
        'description': 'Последняя валидная широта'
    },
    {
        'num': 11,
        'byte': 1,
        'bit': 0b0010_0000,
        'size': 4,
        'description': 'Последняя валидная долгота'
    },
    {
        'num': 12,
        'byte': 1,
        'bit': 0b0001_0000,
        'size': 4,
        'description': 'Последняя валидная высота'
    },
    {
        'num': 13,
        'byte': 1,
        'bit': 0b0000_1000,
        'size': 4,
        'description': 'Скорость'
    },
    {
        'num': 14,
        'byte': 1,
        'bit': 0b0000_0100,
        'size': 2,
        'description': 'Курс'
    },
    {
        'num': 15,
        'byte': 1,
        'bit': 0b0000_0010,
        'size': 4,
        'description': 'Текущий пробег'
    },
    {
        'num': 16,
        'byte': 1,
        'bit': 0b0000_0001,
        'size': 4,
        'description': 'Последний отрезок пути'
    },
    {
        'num': 17,
        'byte': 2,
        'bit': 0b1000_0000,
        'size': 2,
        'description': 'Общее количество секунд на последнем отрезке пути'
    },
    {
        'num': 18,
        'byte': 2,
        'bit': 0b0100_0000,
        'size': 2,
        'description': 'Количество секунд на последнем отрезке пути, по которым вычислялся пробег (валидная навигация)'
    },
    {
        'num': 19,
        'byte': 2,
        'bit': 0b0010_0000,
        'size': 2,
        'description': 'Напряжение на основном источнике питания'
    },
    {
        'num': 20,
        'byte': 2,
        'bit': 0b0001_0000,
        'size': 2,
        'description': 'Напряжение на резервном источнике питания'
    },
    {
        'num': 21,
        'byte': 2,
        'bit': 0b0000_1000,
        'size': 2,
        'description': 'Напряжение на аналоговом входе 1 (Ain1)'
    },
    {
        'num': 22,
        'byte': 2,
        'bit': 0b0000_0100,
        'size': 2,
        'description': 'Напряжение на аналоговом входе 2 (Ain2)'
    },
    {
        'num': 23,
        'byte': 2,
        'bit': 0b0000_0010,
        'size': 2,
        'description': 'Напряжение на аналоговом входе 3 (Ain3)'
    },
    {
        'num': 24,
        'byte': 2,
        'bit': 0b0000_0001,
        'size': 2,
        'description': 'Напряжение на аналоговом входе 4 (Ain4)'
    },
    {
        'num': 25,
        'byte': 3,
        'bit': 0b1000_0000,
        'size': 2,
        'description': 'Напряжение на аналоговом входе 5 (Ain5)'
    },
    {
        'num': 26,
        'byte': 3,
        'bit': 0b0100_0000,
        'size': 2,
        'description': 'Напряжение на аналоговом входе 6 (Ain6)'
    },
    {
        'num': 27,
        'byte': 3,
        'bit': 0b0010_0000,
        'size': 2,
        'description': 'Напряжение на аналоговом входе 7 (Ain7)'
    },
    {
        'num': 28,
        'byte': 3,
        'bit': 0b0001_0000,
        'size': 2,
        'description': 'Напряжение на аналоговом входе 8 (Ain8)'
    },
    {
        'num': 29,
        'byte': 3,
        'bit': 0b0000_1000,
        'size': 1,
        'description': 'Текущие показания дискретных датчиков 1'
    },
    {
        'num': 30,
        'byte': 3,
        'bit': 0b0000_0100,
        'size': 1,
        'description': 'Текущие показания дискретных датчиков 2'
    },
    {
        'num': 31,
        'byte': 3,
        'bit': 0b0000_0010,
        'size': 1,
        'description': 'Текущее состояние выходов 1'
    },
    {
        'num': 32,
        'byte': 3,
        'bit': 0b0000_0001,
        'size': 1,
        'description': 'Текущее состояние выходов 2'
    },
    {
        'num': 33,
        'byte': 4,
        'bit': 0b1000_0000,
        'size': 4,
        'description': 'Показания счетчика импульсов 1'
    },
    {
        'num': 34,
        'byte': 4,
        'bit': 0b0100_0000,
        'size': 4,
        'description': 'Показания счетчика импульсов 2'
    },
    {
        'num': 35,
        'byte': 4,
        'bit': 0b0010_0000,
        'size': 2,
        'description': 'Частота на аналогово-частотном датчике уровня топлива 1'
    },
    {
        'num': 36,
        'byte': 4,
        'bit': 0b0001_0000,
        'size': 2,
        'description': 'Частота на аналогово-частотном датчике уровня топлива 2'
    },
    {
        'num': 37,
        'byte': 4,
        'bit': 0b0000_1000,
        'size': 4,
        'description': 'Моточасы, подсчитанные во время срабатывания датчика работы генератора'
    },
    {
        'num': 38,
        'byte': 4,
        'bit': 0b0000_0100,
        'size': 2,
        'description': 'Уровень топлива, измеренный датчиком уровня топлива 1 RS-485'
    },
    {
        'num': 39,
        'byte': 4,
        'bit': 0b0000_0010,
        'size': 2,
        'description': 'Уровень топлива, измеренный датчиком уровня топлива 2 RS-485'
    },
    {
        'num': 40,
        'byte': 4,
        'bit': 0b0000_0001,
        'size': 2,
        'description': 'Уровень топлива, измеренный датчиком уровня топлива 3 RS-485'
    },
    {
        'num': 41,
        'byte': 5,
        'bit': 0b1000_0000,
        'size': 2,
        'description': 'Уровень топлива, измеренный датчиком уровня топлива 4 RS-485'
    },
    {
        'num': 42,
        'byte': 5,
        'bit': 0b0100_0000,
        'size': 2,
        'description': 'Уровень топлива, измеренный датчиком уровня топлива 5 RS-485'
    },
    {
        'num': 43,
        'byte': 5,
        'bit': 0b0010_0000,
        'size': 2,
        'description': 'Уровень топлива, измеренный датчиком уровня топлива 6 RS-485'
    },
    {
        'num': 44,
        'byte': 5,
        'bit': 0b0001_0000,
        'size': 2,
        'description': ''
    },
    {
        'num': 45,
        'byte': 5,
        'bit': 0b0000_1000,
        'size': 1,
        'description': 'Температура с цифрового датчика 1 (в градусах Цельсия)'
    },
    {
        'num': 46,
        'byte': 5,
        'bit': 0b0000_0100,
        'size': 1,
        'description': 'Температура с цифрового датчика 2 (в градусах Цельсия)'
    },
    {
        'num': 47,
        'byte': 5,
        'bit': 0b0000_0010,
        'size': 1,
        'description': 'Температура с цифрового датчика 3 (в градусах Цельсия)'
    },
    {
        'num': 48,
        'byte': 5,
        'bit': 0b0000_0001,
        'size': 1,
        'description': 'Температура с цифрового датчика 4 (в градусах Цельсия)'
    },
    {
        'num': 49,
        'byte': 6,
        'bit': 0b1000_0000,
        'size': 1,
        'description': 'Температура с цифрового датчика 5 (в градусах Цельсия)'
    },
    {
        'num': 50,
        'byte': 6,
        'bit': 0b0100_0000,
        'size': 1,
        'description': 'Температура с цифрового датчика 6 (в градусах Цельсия)'
    },
    {
        'num': 51,
        'byte': 6,
        'bit': 0b0010_0000,
        'size': 1,
        'description': 'Температура с цифрового датчика 7 (в градусах Цельсия)'
    },
    {
        'num': 52,
        'byte': 6,
        'bit': 0b0001_0000,
        'size': 1,
        'description': 'Температура с цифрового датчика 8 (в градусах Цельсия)'
    },
    {
        'num': 53,
        'byte': 6,
        'bit': 0b0000_1000,
        'size': 2,
        'description': 'CAN Уровень топлива в баке'
    },
    {
        'num': 54,
        'byte': 6,
        'bit': 0b0000_0100,
        'size': 4,
        'description': 'CAN Полный расход топлив'
    },
    {
        'num': 55,
        'byte': 6,
        'bit': 0b0000_0010,
        'size': 2,
        'description': 'CAN Обороты двигателя'
    },
    {
        'num': 56,
        'byte': 6,
        'bit': 0b0000_0001,
        'size': 1,
        'description': 'CAN Температура охлаждающей жидкости (двигателя)'
    },
    {
        'num': 57,
        'byte': 7,
        'bit': 0b1000_0000,
        'size': 4,
        'description': 'CAN Полный пробег ТС'
    },
    {
        'num': 58,
        'byte': 7,
        'bit': 0b0100_0000,
        'size': 2,
        'description': 'CAN Нагрузка на ось 1'
    },
    {
        'num': 59,
        'byte': 7,
        'bit': 0b0010_0000,
        'size': 2,
        'description': 'CAN Нагрузка на ось 2'
    },
    {
        'num': 60,
        'byte': 7,
        'bit': 0b0001_0000,
        'size': 2,
        'description': 'CAN Нагрузка на ось 3'
    },
    {
        'num': 61,
        'byte': 7,
        'bit': 0b0000_1000,
        'size': 2,
        'description': 'CAN Нагрузка на ось 4'
    },
    {
        'num': 62,
        'byte': 7,
        'bit': 0b0000_0100,
        'size': 2,
        'description': 'CAN Нагрузка на ось 5'
    },
    {
        'num': 63,
        'byte': 7,
        'bit': 0b0000_0010,
        'size': 1,
        'description': 'CAN Положение педали газа'
    },
    {
        'num': 64,
        'byte': 7,
        'bit': 0b0000_0001,
        'size': 1,
        'description': 'CAN Положение педали тормоза'
    },
    {
        'num': 65,
        'byte': 8,
        'bit': 0b1000_0000,
        'size': 1,
        'description': 'CAN Нагрузка на двигатель'
    },
    {
        'num': 66,
        'byte': 8,
        'bit': 0b0100_0000,
        'size': 2,
        'description': 'CAN Уровень жидкости в дизельном фильтре выхлопных газов'
    },
    {
        'num': 67,
        'byte': 8,
        'bit': 0b0010_0000,
        'size': 4,
        'description': 'CAN Полное время работы двигателя'
    },
    {
        'num': 68,
        'byte': 8,
        'bit': 0b0001_0000,
        'size': 2,
        'description': 'CAN Расстояние до ТО'
    },
    {
        'num': 69,
        'byte': 8,
        'bit': 0b0000_1000,
        'size': 1,
        'description': 'CAN Скорость ТС'
    }
]


def decode_field(field, value):
    match field['num']:
        case 1 | 2:
            return int.from_bytes(value, "little")
        case 3 | 9:
            return datetime.fromtimestamp(int.from_bytes(value, "little")).strftime("%Y-%m-%d %H:%M:%S")
        case 4 | 5 | 6 | 8 | 17 | 18 | 19 | 20 | 21 | 22 | 23 | 24 | 25 | 26 | 27 | 28 | 29 | 30 | 31 | 32 | 33 | \
                34 | 35 | 36 | 37 | 38 | 39 | 40 | 41 | 42 | 43 | 44 | 55 | 67 | 69:
            return int.from_bytes(value, "little", signed=False)
        case 7:
            i = int.from_bytes(value, "little", signed=False)
            if i < 32:
                return -113 + i * 2
            elif i == 99:
                return None
            else:
                return -51
        case 10 | 11 | 12 | 14 | 45 | 46 | 47 | 48 | 49 | \
                50 | 51 | 52 | 56 | 58 | 59 | 60 | 61 | 62 | 63 | 64 | 65 | 68:
            return int.from_bytes(value, "little", signed=True)
        case 13 | 15 | 16 | 54 | 57:
            return str(struct.unpack('f', value)[0])
        case 53 | 66:
            v = int.from_bytes(value, "little", signed=False)
            if v & 0x8000:  # Уровень в процентах
                return str(v & 0xFF) + '%'
            else:  # Уровень в литрах, с точностью до 0.1 л
                return str(v / 10)
        case _:
            return int.from_bytes(value, "little", signed=False)
