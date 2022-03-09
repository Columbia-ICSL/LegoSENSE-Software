import time
from smbus2 import SMBus
import logging
from threading import Thread, Lock


class TCA9548A(object):
    # Modified from https://github.com/IRNAS/tca9548a-python/blob/master/tca9548a.py
    def __init__(self, bus=1, address=0x70):
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


class EEP(object):
    def __init__(self, lock=None, eep_addr=0x50):
        self.slots_taken = [False, False, False, False]
        self.lock = lock if lock is not None else Lock()
        self.eep_addr = eep_addr

        self.lock.acquire()
        self.mux = TCA9548A()
        self.mux.set_control_register(0b00000000)  # disable all
        self.lock.release()

        self.eep_bus = SMBus(1)
        self.status_thread = Thread(target=self.scan_eep)
        self.status_thread.start()

    def scan_eep(self):
        while True:
            for i in range(4):
                self.lock.acquire()
                self.mux.set_control_register(0b00000000)  # disable all
                self.mux.set_channel(i, 1)
                self.lock.release()
                
                time.sleep(0.2)
                self.lock.acquire()
                try:
                    self.eep_bus.read_byte(self.eep_addr)
                    self.lock.release()
                    self.slots_taken[i] = True
                except KeyboardInterrupt:
                    self.lock.release()
                    exit(1)
                except OSError: # error name
                    self.lock.release()
                    self.slots_taken[i] = False
    
    def get_status(self):
        assert self.status_thread.is_alive(), 'Error: scan_eep thread is dead!'
        return self.slots_taken


if __name__ == "__main__":
    eep = EEP()
    while True:
        time.sleep(1)
        print(eep.get_status())
