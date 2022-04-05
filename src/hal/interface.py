import os
import sys
sys.path.append(os.path.dirname((os.path.dirname(os.path.realpath(__file__)))))

import RPi.GPIO as GPIO

from hal.adc.adc import SensorHubADC
from hal.util import ResourceManager

resource_manager = ResourceManager()

def get_i2c_bus(slot):
    if slot in ['slot1', 'slot2']:
        return 1
    elif slot in ['slot3', 'slot4']:
        return 6
    else:
        raise RuntimeError(f'Invalid slot {slot}!')

def get_spi_bus(slot):
    if slot in ['slot1', 'slot2']:
        return 0
    elif slot in ['slot3', 'slot4']:
        return 1
    else:
        raise RuntimeError(f'Invalid slot {slot}!')

def get_spi_pin_bcm(slot):
    assert slot in ['slot1', 'slot2', 'slot3', 'slot4']
    if slot in ['slot1', 'slot2']:
        cs = 8 if slot == 'slot1' else 7
        miso = 9
        mosi = 10
        sck = 11
    elif slot in ['slot3', 'slot4']:
        cs = 18 if slot == 'slot3' else 17
        miso = 19
        mosi = 20
        sck = 21
    return {
        'mode': GPIO.BCM,
        'cs': cs,
        'miso': miso,
        'mosi': mosi,
        'sck': sck
    }

def get_uart(slot):
    if slot == 'slot1':
        # GPIO 14, 15 -- ALT0 -- UART0
        return '/dev/ttyS0'
    elif slot == 'slot2':
        # GPIO 0, 1 -- ALT4 -- UART2
        return '/dev/ttyAMA1'
    elif slot == 'slot3':
        # GPIO 4, 5 -- ALT4 -- UART3
        return '/dev/ttyAMA2'
    elif slot == 'slot4':
        # GPIO 12, 13 -- ALT4 -- UAR5
        return '/dev/ttyAMA3'

def get_reset(slot):
    if slot == 'slot1':
        return 24
    elif slot == 'slot2':
        return 25
    elif slot == 'slot3':
        return 26
    elif slot == 'slot4':
        return 27

class SensorHubInterface:
    def __init__(self, slot):
        self.slot = slot
        self.adc = SensorHubADC()

    @property
    def i2c_bus(self):
        return get_i2c_bus(self.slot)

    @property
    def spi_bus(self):
        return get_spi_bus(self.slot)

    @property
    def spi_pins_bcm(self):
        return get_spi_pin_bcm(self.slot)

    @property
    def uart(self):
        return get_uart(self.slot)

    @property
    def pin_rst(self):
        return get_reset(self.slot)

    def read_adc(self, channel):
        assert channel in [0, 1]
        with resource_manager.lock('I2C', 1):
            return self.adc.read(int(self.slot[-1]), channel)

    def from_str(self, interface_name):
        if interface_name.upper() == 'I2C':
            return self.i2c_bus
        if interface_name.upper() == 'SPI':
            return self.spi_bus
        elif interface_name.upper() == 'UART':
            return self.uart
        elif interface_name.upper() == 'RST':
            return self.pin_rst
        else:
            raise ValueError(f'Invalid interface {interface_name}. Expected `I2C`, `UART`, or `RST`')
