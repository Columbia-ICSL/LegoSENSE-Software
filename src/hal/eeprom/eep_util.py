import time
from smbus2 import SMBus
import logging
from threading import Thread, Lock

try:
    from hal.eeprom.eeprom import EEPROM
except:
    from eeprom import EEPROM

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
    EEP_BUS = 1
    def __init__(self, lock=None, eep_addr=0x50):
        self.slots_taken = [None, None, None, None]
        self.module_names = {1: "", 2: "", 3: "", 4: ""}
        self.lock = lock if lock is not None else Lock()
        self.eep_addr = eep_addr

        with self.lock:
            self.mux = TCA9548A()
            self.mux.set_control_register(0b00000000)  # disable all

        self.eep_bus = SMBus(1)
        self.status_thread = Thread(target=self.scan_eep)
        self.status_thread.start()

    def scan_eep(self):
        while True:
            for i in range(4):
                with self.lock:
                    self.mux.set_control_register(0b00000000)  # disable all
                    self.mux.set_channel(i, 1)
                
                # First run: quick scan no delay
                if self.slots_taken[i] is not None:
                    time.sleep(0.2)
                try:
                    with self.lock:
                        self.eep_bus.read_byte(self.eep_addr)
                    self.slots_taken[i] = True
                    module_name = self.read_eep(i+1)
                    self.module_names[i+1] = "UnrecognizedModule" if module_name is None else module_name.decode()
                except KeyboardInterrupt:
                    exit(1)
                except OSError: # error name
                    self.slots_taken[i] = False
                    self.module_names[i+1] = ""
                except ValueError: # ValueError: I2C device not exist on: 0x50
                    self.slots_taken[i] = False
                    self.module_names[i+1] = ""
    
    def get_status(self):
        assert self.status_thread.is_alive(), 'Error: scan_eep thread is dead!'
        return self.slots_taken, self.module_names

    def write_eep(self, idx, val, check_integrity=True):
        assert 1 <= idx <= 4, f'Slots must be between 1 and 4: got {idx}'
        # 2Kb EEPROM = 2048 bits = 256 bytes. Use 1st byte for length - max len 255 bytes
        assert len(val) <= 255, f'Data trying to write will not fit in 2Kb EEPROM!'
        assert self.slots_taken[idx-1], f'Daughterboard / EEPROM not detected on slot {idx}'

        to_write = b''
        to_write += len(val).to_bytes(1, 'big')
        to_write += val.encode('ascii')
        
        with self.lock:
            self.mux.set_control_register(0b00000000)  # disable all
            self.mux.set_channel(idx-1, 1)
            eeprom = EEPROM("24c02", self.EEP_BUS, self.eep_addr)
            eeprom.write(to_write)

        # if check_integrity:
        #     readback = self.read_eep(idx)
        #     assert to_write == readback, f'Written ->{to_write}<-, got ->{readback}<-'
    
    def read_eep(self, idx):
        assert 1 <= idx <= 4, f'Slots must be between 1 and 4: got {idx}'
        assert self.slots_taken[idx-1], f'Daughterboard / EEPROM not detected on slot {idx}'

        with self.lock:
            self.mux.set_control_register(0b00000000)  # disable all
            self.mux.set_channel(idx-1, 1)
            eeprom = EEPROM("24c02", self.EEP_BUS, self.eep_addr)
            data_length = int.from_bytes(eeprom.read(size=1, addr=0), "big")
            assert 0 <= data_length <= 255
            data = eeprom.read(size=data_length, addr=1)

        # print(f'Data length={data_length}, data={data}')
        if data_length == 255 and 0xFF in data:  # Uninitialized EEPROM
            return None
        return data


if __name__ == "__main__":
    eep = EEP()
    while True:
        time.sleep(1)
        print(eep.get_status())
