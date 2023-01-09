# Тестирование декодера пакетов и модуля хранения
from constants import PACKET_TYPE_A, PACKET_TYPE_C
from consumer import Consumer
from packet_decoder import decode_packet, decode_flex_message
import pprint
from config import config

pp = pprint.PrettyPrinter(compact=True)
consumer = Consumer(config)

with open('test/HANDSHAKE_862531045630978', mode="rb") as f:
    data = f.read()
    res = decode_packet(data)
    client_id = res['client_id']

with open('test/VERSION_APPROVAL', mode="rb") as f:
    data = f.read()
    res = decode_packet(data)
    print(res['message'])
    fields = res['fields']
    structure_length = res['structure_length']
    print(f'structure_length: {structure_length}')
    print(fields)

with open('test/PACKET_C', mode="rb") as f:
    data = f.read()
    res = decode_packet(data)
    print(res['message'])
    message = decode_flex_message(fields, res['payload'])
    consumer.consume_flex_message(client_id, PACKET_TYPE_C, message)
    # print(s['1'], s['2'], s['3'], s['19'], s['20'], s['45'])

with open('test/PACKET_A_8_RECORDS', mode="rb") as f:
    data = f.read()
    res = decode_packet(data)
    print(res['message'])
    records_count = res['records_count']
    data = res['payload']
    for i in range(records_count):
        message = decode_flex_message(fields, data[i * structure_length: (i + 1) * structure_length])
        consumer.consume_flex_message(client_id, PACKET_TYPE_A, message)
        # pp.pprint(s)
        # print(s['1'], s['2'], s['3'], s['19'], s['20'], s['45'])
