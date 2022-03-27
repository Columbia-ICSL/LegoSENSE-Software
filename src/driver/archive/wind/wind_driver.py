import os
import sys
import time

sys.path.append(os.path.dirname((os.path.dirname(os.path.dirname(os.path.realpath(__file__))))))
from driver.driver_template import SensorHubModuleTemplate

from archive.wind.wind import ADS1115, i2c_driver

WindModuleSensors = ['wind']
WindModuleSensorsColumns = {
    'wind': ['Wind Speed'],
}

class WindModule(SensorHubModuleTemplate):
    def __init__(self, config_path, interface):
        print('WindModule init')
        super().__init__(config_path, interface)

        # TODO: support other channels
        self.adc = ADS1115(i2c=i2c_driver(1))
        self.adc.start_adc(0, gain=(2/3))

    def setup_config(self):
        self.fs = float(self.get_config('Wind Sensor', 'SamplingFrequency'))

    def read(self, sensor):
        if sensor == 'wind':
            value = round((self.adc.read_adc(0, gain=(2/3)) / 32768) * 6.144, 3)
            return {'_t': time.time(), 'Wind Speed': value}
        else:
            return f'{sensor}: not implemented'

    def wait_for_next_sample(self):
        time.sleep(1 / self.fs)
        return WindModuleSensors
