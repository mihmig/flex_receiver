# Модуль хранения пакетов данных
from constants import PACKET_TYPE_PING, PACKET_TYPE_A, PACKET_TYPE_C, PACKET_TYPE_HANDSHAKE, PACKET_TYPE_APPROVAL, \
    PACKET_TYPE_T


class Consumer:
    def __init__(self, config: dict):
        self.config = config
        self.bot_token = config['telegram']['bot_token']
        self.fields_to_show = config['fields_to_show']

    # Обрабатывает двоичные данные принятые от устройства (для отладки)
    def consume_binary_data(self):
        pass

    # Обрабатывает FLEX-сообщение
    def consume_flex_message(self, client_id: str, packet_type: str, message: dict | None):
        print(f'packet_type = {packet_type} client_id={client_id}')

        if packet_type == PACKET_TYPE_PING:
            # TODO update last device online moment
            print('consumed PING')
        elif packet_type == PACKET_TYPE_HANDSHAKE:
            print('consumed HANDSHAKE')
        elif packet_type == PACKET_TYPE_APPROVAL:
            print('consumed PACKET_TYPE_APPROVAL')
        elif packet_type == PACKET_TYPE_A:
            self.debug_message(client_id, message)
        elif packet_type == PACKET_TYPE_C:
            self.debug_message(client_id, message)
        elif packet_type == PACKET_TYPE_T:
            self.debug_message(client_id, message)

    # Выводит отдельные поля сообщения в консоль
    def debug_message(self, client_id: str, message: dict):
        f = []
        for i in self.fields_to_show:
            if i in message:
                f.append(message[i])
            else:
                f.append('~')
        print(client_id, '\t\t'.join(str(x) for x in f))
