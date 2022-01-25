# https://github.com/ARizzo35/python-eeprom
from eeprom import EEPROM

bus = 1
device = 0x50

eeprom = EEPROM("24c02", bus, device)

test_string = "1"
test_length = len(test_string)

eeprom.write(test_string.encode())
verify = eeprom.read(test_length).decode()

print(verify)

assert verify == test_string