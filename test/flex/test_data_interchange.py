# Тестирование цикла обмена данными
import socket

from plugins.constants import LOCAL_PORT

socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket.connect(('localhost', LOCAL_PORT))
with open('test/HANDSHAKE_862531045630978', mode="rb") as f:
    data = f.read()
    print('sending HANDSHAKE')
    socket.send(data)
    answer = socket.recv(4096)
    print(f"received answer: {answer.hex(' ', 1)}")

with open('test/VERSION_APPROVAL', mode="rb") as f:
    data = f.read()
    print('sending VERSION_APPROVAL')
    socket.send(data)
    answer = socket.recv(4096)
    print(f"received answer: {answer.hex(' ', 1)}")

# with open('test/PACKET_A_8_RECORDS', mode="rb") as f:
#     data = f.read()
#     print('sending PACKET_A_8_RECORDS')
#     socket.send(data)
#     answer = socket.recv(4096)
#     print(f"received answer: {answer.hex(' ', 1)}")
#
# with open('test/PACKET_C', mode="rb") as f:
#     data = f.read()
#     print('sending PACKET_C')
#     socket.send(data)
#     answer = socket.recv(4096)
#     print(f"received answer: {answer.hex(' ', 1)}")

# with open('temp/data_17', mode="rb") as f:
#     data = f.read()
#     print('sending PACKET_C')
#     socket.send(data)
#     answer = socket.recv(4096)
#     print(f"received answer: {answer.hex(' ', 1)}")
