# Получение данных от GPS-трекеров по протоколу FLEX
# 193.193.165.165 21626
# 46.229.188.134 21626
import socket
import sys
import threading
from datetime import datetime
from crc8_flex import crc8
from config import config
from consumer import Consumer

from constants import *
from packet_decoder import decode_packet, decode_flex_message

consumer = Consumer(config)


def log(line: str):
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), ' ', line)


def receive_from_socket(s):
    # receive data from a socket until no more data is there
    b = b""
    while True:
        data = s.recv(4096)
        b += data
        if not data or len(data) < 4096:
            break
    return b


def flex_thread(local_socket, client_info):
    client_id = ''
    fields = []
    structure_length = 0
    while True:
        data = receive_from_socket(local_socket)
        if not data:
            print(f'THREAD: client: {client_info} disconnected')
            break
        # Обработка пакетов
        res = decode_packet(data)
        if 'packet_type' not in res:
            print('THREAD: during packet decoding: ', res)
            continue
        packet_type = res['packet_type']
        # print(f"received packet: type={res['packet_type']}")

        # if 'message' in res:
        #     print(res['message'])

        if packet_type == PACKET_TYPE_PING:
            consumer.consume_flex_message(client_id, packet_type, res['message'])
        elif packet_type == PACKET_TYPE_A:
            local_socket.send(data[0:3] + crc8(data[0:3]).to_bytes(1, "little"))
            records_count = res['records_count']
            payload = res['payload']
            for i in range(records_count):
                message = decode_flex_message(fields, payload[i * structure_length: (i + 1) * structure_length])
                consumer.consume_flex_message(client_id, packet_type, message)
        elif packet_type == PACKET_TYPE_C:
            local_socket.send(PACKET_C_ANSWER)
            message = decode_flex_message(fields, res['payload'])
            consumer.consume_flex_message(client_id, packet_type, message)
        elif packet_type == PACKET_TYPE_T:
            local_socket.send(data[0:2] + crc8(data[0:6]).to_bytes(1, "little"))
            message = decode_flex_message(fields, res['payload'])
            consumer.consume_flex_message(client_id, packet_type, message)
        elif packet_type == PACKET_TYPE_HANDSHAKE:
            local_socket.send(HANDSHAKE_ANSWER)
            client_id = res['client_id']
            consumer.consume_flex_message(client_id, packet_type, None)
        elif packet_type == PACKET_TYPE_APPROVAL:
            fields = res['fields']
            structure_length = res['structure_length']
            local_socket.send(VERSION_APPROVAL_ANSWER)
            continue
        elif packet_type == PACKET_TYPE_ERROR:
            local_socket.close()
            return
        else:
            print('THREAD: unknown decoded packet type: ', res)
            continue


def main():
    flex_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    flex_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        flex_socket.bind(('0.0.0.0', LOCAL_PORT))
    except socket.error as e:
        log(e.strerror)
        sys.exit(5)
    flex_socket.listen(100)
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


if __name__ == '__main__':
    main()
