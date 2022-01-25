import time
from smbus2 import SMBus
import logging


class TCA9548A(object):
    # Modified from https://github.com/IRNAS/tca9548a-python/blob/master/tca9548a.py
    def __init__(self, bus, address):
        """Init smbus channel and tca driver on specified address."""
        try:
            self.PORTS_COUNT = 8     # number of switches

            self.i2c_bus = SMBus(bus)
            self.i2c_address = address
            if self.get_control_register() is None:
                raise ValueError
        except ValueError:
            logging.error("No device found on specified address!")
            self.i2c_bus = None
        except:
            logging.error("Bus on channel {} is not available.".format(I2C_CHANNEL))
            logging.info("Available busses are listed as /dev/i2c*")
            self.i2c_bus = None

    def get_control_register(self):
        """Read value (length: 1 byte) from control register."""
        try:
            value = self.i2c_bus.read_byte(self.i2c_address)
            return value
        except:
            return None

    def get_channel(self, ch_num):
        """Get channel state (specified with ch_num), return 0=disabled or 1=enabled."""
        if ch_num < 0 or ch_num > self.PORTS_COUNT:
            return None
        register = self.get_control_register()
        if register is None:
            return None
        value = ((register >> ch_num) & 1)
        return value

    def set_control_register(self, value):
        """Write value (length: 1 byte) to control register."""
        try:
            if value < 0 or value > 255:
                return False
            self.i2c_bus.write_byte(self.i2c_address, value)
            return True
        except:
            return False

    def set_channel(self, ch_num, state):
        """Change state (0=disable, 1=enable) of a channel specified in ch_num."""
        if ch_num < 0 or ch_num > self.PORTS_COUNT:
            return False
        if state != 0 and state != 1:
            return False
        current_value = self.get_control_register()
        if current_value is None:
            return False
        if state:
            new_value = current_value | 1 << ch_num
        else:
            new_value = current_value & (255 - (1 << ch_num))
        return_value = self.set_control_register(new_value)
        return return_value

    def __del__(self):
        """Driver destructor."""
        self.i2c_bus = None


i2c_bus = 1
i2c_address = 0x70
tca_driver = TCA9548A(i2c_bus, i2c_address)


from eeprom import EEPROM
eeprom = EEPROM("24c02", 1, 0x50)


while True:
    for i in range(4):
        tca_driver.set_control_register(0b00000000)  # disable all
        tca_driver.set_channel(i, 1)

        test_string = str(i)
        test_length = len(test_string)

        # eeprom.write(test_string.encode())
        verify = eeprom.read(test_length).decode()

        print(verify)

        # assert verify == test_string

        time.sleep(1)
