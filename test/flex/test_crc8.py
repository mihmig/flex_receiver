from crc8_flex import crc8

message = bytearray(b'\x7E\x41\x08')
assert crc8(message) == 0x57
message = bytearray(b'\x7E\x43')
assert crc8(message) == 0xB9
