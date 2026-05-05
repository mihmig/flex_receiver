# Описание полей FLEX-структуры и методы для их декодирования
import struct
import plugins.flex_constants as c

def decode_field(field: dict, value: bytes):
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
             c.FIELD_CAN_FULL_FUEL_CONSUMPTION | \
             c.FIELD_CAN_FULL_VEHICLE_MILEAGE:
            return str(struct.unpack('f', value)[0])
        case c.FIELD_NAVIGATION_INFO:
            return {
                "glonass": value[0],
                "GPS": value[1]
                # "Galileo": value[2],
                # "Compass": value[3],
                # "Beidou": value[4],
                # "DORIS": value[5],
                # "IRNSS": value[6],
                # "QZSS": value[7]
            }
        case c.FIELD_LBS_INFO:
            return {
                "cell_id": int.from_bytes(value[0:4], "little", signed=False),
                "lac": int.from_bytes(value[4:6], "little", signed=False),
                "mcc": int.from_bytes(value[6:8], "little", signed=False),
                "mnc": int.from_bytes(value[8:10], "little", signed=False),
                "dbm": int.from_bytes(value[10:11], "little", signed=True),
                "cell_id1": int.from_bytes(value[11:15], "little", signed=False),
                "lac1": int.from_bytes(value[15:17], "little", signed=False),
                "mcc1": int.from_bytes(value[17:19], "little", signed=False),
                "mnc1": int.from_bytes(value[19:21], "little", signed=False),
                "dbm1": int.from_bytes(value[21:22], "little", signed=True),
                "cell_id2": int.from_bytes(value[22:26], "little", signed=False),
                "lac2": int.from_bytes(value[26:28], "little", signed=False),
                "mcc2": int.from_bytes(value[28:30], "little", signed=False),
                "mnc2": int.from_bytes(value[30:32], "little", signed=False),
                "dbm2": int.from_bytes(value[32:33], "little", signed=True),
                "timestamp": int.from_bytes(value[33:38], "little", signed=False)
            }
        case c.FIELD_HDOP_PDOP:
            return {
               "HDOP": value[0] / 10,
               "PDOP": value[1] / 10
            }
        case c.FIELD_HIGH_PRECISION_SENSOR_STATE | \
             c.FIELD_HIGH_PRECISION_LAT_LON | \
             c.FIELD_HIGH_PRECISION_ALT | \
             c.FIELD_HIGH_PRECISION_DIRECTION | \
             c.FIELD_HIGH_PRECISION_SPEED:
            return 0 # Значения игнорируем
        case c.FIELD_CAN_FUEL_LEVEL | \
             c.FIELD_CAN_LIQUID_LEVEL_DIESEL_EXHAUST_FILTER:
            v = int.from_bytes(value, "little", signed=False)
            if v & 0x8000:  # Уровень в процентах
                return str(v & 0xFF) + '%'
            else:  # Уровень в литрах, с точностью до 0.1 л
                return str(v / 10)
        case _:
            return int.from_bytes(value, "little", signed=False)
