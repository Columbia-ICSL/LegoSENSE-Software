import os
import sys
# sys.path.append(os.path.dirname((os.path.dirname(os.path.dirname(os.path.realpath(__file__))))))
import time
from smbus2 import SMBus
try:
    from hal.adc.ads1115 import ADS1115
except:
    from ads1115 import ADS1115

class i2c_driver:
    def __init__(self, bus):
        print("ADC INIT!!!!!!!!!!")
        self.bus = bus
        self.address = None
        pass
    def get_i2c_device(self, address, **kwargs):
        self.address = address
        return self
    def writeList(self, reg, data):
        assert self.address is not None
        with SMBus(self.bus) as bus:
            bus.write_i2c_block_data(self.address, reg, data)
    def readList(self, reg, read_len):
        assert self.address is not None
        with SMBus(self.bus) as bus:
            data = bus.read_i2c_block_data(self.address, reg, read_len)
        return data


class SensorHubADC():
    def __init__(self):
        self.adc_1 = ADS1115(address=0x48, i2c=i2c_driver(1))
        self.adc_2 = ADS1115(address=0x49, i2c=i2c_driver(1))
        self.adc_1.start_adc(0, gain=(2/3))
        self.adc_2.start_adc(0, gain=(2/3))
        self.adc_mapping = {
            1: {0: (self.adc_1, 0), 1: (self.adc_1, 1)},
            2: {0: (self.adc_2, 0), 1: (self.adc_2, 1)},
            3: {0: (self.adc_1, 2), 1: (self.adc_1, 3)},
            4: {0: (self.adc_2, 2), 1: (self.adc_2, 3)}
        }
    
    def read(self, module, channel):
        assert module in [1, 2, 3, 4], f'Module number must be in [1, 2, 3, 4]'
        assert channel in [0, 1], f'Channel index must be in [0, 1]'
        adc, ch = self.adc_mapping[module][channel]
        return (adc.read_adc(ch, gain=(2/3)) / 32768) * 6.144


if __name__ == "__main__":
    adc = SensorHubADC()
    print('|  M1A0 |  M1A1 |  M2A0 |  M2A1 |  M3A0 |  M3A1 |  M4A0 |  M4A1 |')
    print('-' * 65)
    # Main loop.
    while True:
        # Read all the ADC channel values in a list.
        values = [
            adc.read(1, 0),
            adc.read(1, 1),
            adc.read(2, 0),
            adc.read(2, 1),
            adc.read(3, 0),
            adc.read(3, 1),
            adc.read(4, 0),
            adc.read(4, 1)
        ]
        print('| {0:.3f} | {1:.3f} | {2:.3f} | {3:.3f} | {4:.3f} | {5:.3f} | {6:.3f} | {7:.3f} |'.format(*values))
        time.sleep(0.01)
