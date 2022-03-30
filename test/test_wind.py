import time
from smbus2 import SMBus
from ads1115 import ADS1115

class i2c_driver:
    def __init__(self, bus):
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

adc = ADS1115(i2c=i2c_driver(1))
adc.start_adc(0, gain=(2/3))
print('Reading ADS1x15 values, press Ctrl-C to quit...')
# Print nice channel column headers.
print('| {0:>5} | {1:>5} | {2:>5} | {3:>5} |'.format(*range(4)))
print('-' * 33)
# Main loop.

idx = 0
while True:
    # Read all the ADC channel values in a list.
    values = [0]*4
    for i in range(4):
        # Read the specified ADC channel using the previously set gain value.
        values[i] = (adc.read_adc(i, gain=(2/3)) / 32768) * 6.144

        # Note you can also pass in an optional data_rate parameter that controls
        # the ADC conversion time (in samples/second). Each chip has a different
        # set of allowed data rate values, see datasheet Table 9 config register
        # DR bit values.
        #values[i] = adc.read_adc(i, gain=GAIN, data_rate=128)
        # Each value will be a 12 or 16 bit signed integer value depending on the
        # ADC (ADS1015 = 12-bit, ADS1115 = 16-bit).
    # Print the ADC values.
    idx += 1
    raw = values[0]
    print(f'{idx},{raw:.3f}')
    # Pause for half a second.
    time.sleep(0.01)