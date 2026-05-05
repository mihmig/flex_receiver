# Получение данных от GPS-трекеров Navtelecom по протоколу FLEX
import socket
import sys
import threading

import schedule
import time

from plugins.alert_service import AlertService
from plugins.aquarium import Aquarium
from plugins.flex_constants import HANDSHAKE_ANSWER, VERSION_APPROVAL_ANSWER_1, PACKET_C_ANSWER, PACKET_TYPE_HANDSHAKE, \
    PACKET_TYPE_APPROVAL, PACKET_TYPE_PING, PACKET_TYPE_A, PACKET_TYPE_C, PACKET_TYPE_T, PACKET_TYPE_ERROR, \
    PACKET_TYPE_X, PACKET_TYPE_E, VERSION_APPROVAL_ANSWER
from plugins.logger import log
from plugins.crc8_flex import crc8
from plugins.consumer import Consumer

from plugins.constants import *
from plugins.packet_decoder import decode_packet, decode_flex_message
from plugins.max_sender import MaxSender
from plugins.monitoring_service import MonitoringService
from plugins.spoofing_zone_filter import SpoofingZoneFilter
from plugins.storage import Storage
from plugins.telegram_sender import TelegramSender
from plugins.timeout_checker import Checker

def receive_from_socket(s):
    # receive data from a socket until no more data is there
    b = b""
    while True:
        data = s.recv(4096)
        b += data
        if not data or len(data) < 4096:
            break
    return b


def flex_thread(local_socket, p_client_info):
    imei = ''
    fields = []
    structure_length = 0
    while True:
        data = receive_from_socket(local_socket)
        if not data:
            log(f'THREAD: client: {p_client_info} disconnected')
            break
        # Обработка пакетов
        res = decode_packet(data)
        if 'packet_type' not in res:
            log(f"THREAD: during packet decoding: {res['message']}")
            continue
        packet_type = res['packet_type']

        if packet_type == PACKET_TYPE_PING:
            consumer.consume_flex_message(imei, packet_type, None, None)
        elif packet_type == PACKET_TYPE_A or packet_type == PACKET_TYPE_E:
            local_socket.send(data[0:3] + crc8(data[0:3]).to_bytes(1, "little"))
            records_count = res['records_count']
            payload = res['payload']
            for i in range(records_count):
                packet_data = payload[i * structure_length: (i + 1) * structure_length]
                message = decode_flex_message(fields, packet_data)
                consumer.consume_flex_message(imei, packet_type, packet_data, message)
        elif packet_type == PACKET_TYPE_C:
            local_socket.send(PACKET_C_ANSWER)
            message = decode_flex_message(fields, res['payload'])
            consumer.consume_flex_message(imei, packet_type, data, message)
        elif packet_type == PACKET_TYPE_T or packet_type == PACKET_TYPE_X:
            local_socket.send(data[0:6] + crc8(data[0:6]).to_bytes(1, "little"))
            message = decode_flex_message(fields, res['payload'])
            consumer.consume_flex_message(imei, packet_type, data, message)
        elif packet_type == PACKET_TYPE_HANDSHAKE:
            local_socket.send(HANDSHAKE_ANSWER)
            imei = res['imei']
            consumer.consume_flex_message(imei, packet_type, data, res)
        elif packet_type == PACKET_TYPE_APPROVAL:
            fields = res['fields']
            structure_length = res['structure_length']
            local_socket.send(VERSION_APPROVAL_ANSWER + res['protocol_version_code'] + res['struct_version_code'])
            consumer.consume_flex_message(imei, packet_type, data, res)
        elif packet_type == PACKET_TYPE_ERROR:
            if imei.isdigit():
                consumer.consume_flex_message(imei, packet_type, data, res)
            local_socket.close()
            return
        else:
            print('THREAD: unknown decoded packet type: ', res)
            continue


def schedule_thread():
    while True:
        n = schedule.idle_seconds()
        if n is None:
            time.sleep(30)
        elif n > 0:
            time.sleep(n)
        schedule.run_pending()


storage = Storage()
telegram_sender = TelegramSender(storage)
max_sender = MaxSender(storage)
alert_service = AlertService(storage, telegram_sender, max_sender)
monitoring_service = MonitoringService(storage, alert_service)
spoofing_zone_filter = SpoofingZoneFilter(storage)
consumer = Consumer(storage, monitoring_service, spoofing_zone_filter)

checker = Checker(storage, alert_service)
aquarium = Aquarium(storage, alert_service)

flex_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
flex_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
try:
    port = int(storage.get_system_param('local_port') or '21626')
    flex_socket.bind(('0.0.0.0', port))
    log(f'Listening on port: {port}')
except socket.error as e:
    log(e.strerror)
    sys.exit(5)
flex_socket.listen(100)

threading.Thread(target=schedule_thread, daemon=True).start()

try:
    while True:
        in_socket, in_addrinfo = flex_socket.accept()
        client_info = ':'.join(map(lambda x: str(x or ''), in_addrinfo))
        log(f'Connection from {in_addrinfo}')
        _ = threading.Thread(target=flex_thread,
                             args=(in_socket, client_info)).start()
except KeyboardInterrupt:
    log('Ctrl+C detected, exiting...')
    sys.exit(0)
