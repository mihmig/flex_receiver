# Описание полей FLEX-структуры и методы для их декодирования
import struct
import plugins.flex_constants as c

def decode_field(field: dict, value):
    match field['num']:
        case c.FIELD_EEPROM_NUMBER | c.FIELD_EVENT_CODE:
            return int.from_bytes(value, "little")
        case c.FIELD_EVENT_TIME | c.FIELD_LAST_VALID_COORDINATES_TIME:
            return int.from_bytes(value, "little")
        case c.FIELD_DEVICE_STATUS | \
             c.FIELD_FUNC_MODULES_1_STATUS | \
             c.FIELD_FUNC_MODULES_2_STATUS | \
             c.FIELD_GSM_LEVEL | \
             c.FIELD_GPS_LEVEL | \
             c.FIELD_TOTAL_LAST_LAG_SECONDS | \
             c.FIELD_TOTAL_LAST_VALID_LAG_SECONDS | \
             c.FIELD_MAIN_SOURCE_VOLTAGE | \
             c.FIELD_RESERVED_SOURCE_VOLTAGE | \
             c.FIELD_ANALOG_INPUT_1_VOLTAGE | \
             c.FIELD_ANALOG_INPUT_2_VOLTAGE | \
             c.FIELD_ANALOG_INPUT_3_VOLTAGE | \
             c.FIELD_ANALOG_INPUT_4_VOLTAGE | \
             c.FIELD_ANALOG_INPUT_5_VOLTAGE | \
             c.FIELD_ANALOG_INPUT_6_VOLTAGE | \
             c.FIELD_ANALOG_INPUT_7_VOLTAGE | \
             c.FIELD_ANALOG_INPUT_8_VOLTAGE | \
             c.FIELD_DISCRETE_SENSOR_1 | \
             c.FIELD_DISCRETE_SENSOR_2 | \
             c.FIELD_OUTPUT_STATE_1 | \
             c.FIELD_OUTPUT_STATE_2 | \
             c.FIELD_COUNTER_1 | \
             c.FIELD_COUNTER_2 | \
             c.FIELD_AFF_SENSOR_1 | \
             c.FIELD_AFF_SENSOR_2 | \
             c.FIELD_MOTO_HOURS | \
             c.FIELD_FUEL_LEVEL_1 | \
             c.FIELD_FUEL_LEVEL_2 | \
             c.FIELD_FUEL_LEVEL_3 | \
             c.FIELD_FUEL_LEVEL_4 | \
             c.FIELD_FUEL_LEVEL_5 | \
             c.FIELD_FUEL_LEVEL_6 | \
             c.FIELD_UNKNOWN | \
             c.FIELD_CAN_ENGINE_SPEED | \
             c.FIELD_CAN_FULL_ENGINE_OPERATING_TIME | \
             c.FIELD_CAN_VEHICLE_SPEED:
            return int.from_bytes(value, "little", signed=False)
        case 7:
            i = int.from_bytes(value, "little", signed=False)
            if i < 32:
                return -113 + i * 2
            elif i == 99:
                return None
            else:
                return -51
        case c.FIELD_LAST_VALID_LATITUDE | \
             c.FIELD_LAST_VALID_LONGITUDE | \
             c.FIELD_LAST_VALID_ALTITUDE | \
             c.FIELD_DIRECTION | \
             c.FIELD_DIGITAL_TEMP_SENSOR_1 | \
             c.FIELD_DIGITAL_TEMP_SENSOR_2 | \
             c.FIELD_DIGITAL_TEMP_SENSOR_3 | \
             c.FIELD_DIGITAL_TEMP_SENSOR_4 | \
             c.FIELD_DIGITAL_TEMP_SENSOR_5 | \
             c.FIELD_DIGITAL_TEMP_SENSOR_6 | \
             c.FIELD_DIGITAL_TEMP_SENSOR_7 | \
             c.FIELD_DIGITAL_TEMP_SENSOR_8 | \
             c.FIELD_CAN_ENGINE_COOLANT_TEMP | \
             c.FIELD_CAN_AXLE_LOAD_1 | \
             c.FIELD_CAN_AXLE_LOAD_2 | \
             c.FIELD_CAN_AXLE_LOAD_3 | \
             c.FIELD_CAN_AXLE_LOAD_4 | \
             c.FIELD_CAN_AXLE_LOAD_5 | \
             c.FIELD_GAS_PEDAL_POSITION | \
             c.FIELD_CAN_BREAK_PEDAL_POSITION | \
             c.FIELD_CAN_ENGINE_LOAD | \
             c.FIELD_CAN_DISTANCE_TO_INSPECTION:
            return int.from_bytes(value, "little", signed=True)
        case c.FIELD_SPEED | \
             c.FIELD_CURRENT_MILEAGE | \
             c.FIELD_LAST_LEG | \
             c.FIELD_CAN_FULL_FUEL_CONSUMPTION54 | \
             c.FIELD_CAN_FULL_VEHICLE_MILEAGE:
            return str(struct.unpack('f', value)[0])
        case c.FIELD_CAN_FUEL_LEVEL | \
             c.FIELD_CAN_LIQUID_LEVEL_DIESEL_EXHAUST_FILTER:
            v = int.from_bytes(value, "little", signed=False)
            if v & 0x8000:  # Уровень в процентах
                return str(v & 0xFF) + '%'
            else:  # Уровень в литрах, с точностью до 0.1 л
                return str(v / 10)
        case _:
            return int.from_bytes(value, "little", signed=False)
