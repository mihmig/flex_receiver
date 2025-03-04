# Тестирование декодера пакетов и модуля хранения
from packet_decoder import decode_packet

with open('test/1207', mode="rb") as f:
    data = f.read()
    res = decode_packet(data)
    imei = res['imei']
    print(imei)
exit(1)

pp = pprint.PrettyPrinter(compact=True)
sender = Sender(config['telegram'])
storage = Storage(config)
consumer = Consumer(config, storage, sender)
# print(consumer)
object_methods = [method_name for method_name in dir(consumer)
                  if callable(getattr(consumer, method_name))]
print(object_methods)
with open('test/HANDSHAKE_862531045630978', mode="rb") as f:
    data = f.read()
    res = decode_packet(data)
    imei = res['imei']

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
    consumer.consume_flex_message(imei, PACKET_TYPE_C, message)
    # print(s['1'], s['2'], s['3'], s['19'], s['20'], s['45'])

with open('test/PACKET_A_8_RECORDS', mode="rb") as f:
    data = f.read()
    res = decode_packet(data)
    print(res['message'])
    records_count = res['records_count']
    data = res['payload']
    for i in range(records_count):
        message = decode_flex_message(fields, data[i * structure_length: (i + 1) * structure_length])
        consumer.consume_flex_message(imei, PACKET_TYPE_A, message)
        # pp.pprint(s)
        # print(s['1'], s['2'], s['3'], s['19'], s['20'], s['45'])
