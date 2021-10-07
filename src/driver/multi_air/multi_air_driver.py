import os
import sys
import time
from configparser import ConfigParser

sys.path.append(os.path.dirname((os.path.dirname(os.path.dirname(os.path.realpath(__file__))))))
from driver.driver_template import SensorHubModuleTemplate

from driver.multi_air.hdc2080 import Pi_HDC2080
MultiAirModuleSensors = ['airQua', 'TempHum', 'CO2']


class MultiAirModule(SensorHubModuleTemplate):
    def __init__(self, config_path, interface):
        self.config = ConfigParser()
        self.config.read(config_path)
        self.fs = float(self.config['Temperature Humidity']['SamplingFrequency'])

        self.temp_hum = Pi_HDC2080(twi=interface.i2c_bus)
        self.temp_hum.readHumidity()

        print('MultiAirModule init')
        super().__init__(config_path, interface)

    def read(self, sensor):
        if sensor == 'TempHum':
            hum = self.temp_hum.readHumidity()
            tem = self.temp_hum.readTemperature()
            return f'{tem:.2f}\t{hum:.2f}\n'
        else:
            return f'{sensor}: not implemented'

    def wait_for_next_sample(self):
        time.sleep(1 / self.fs)
        return MultiAirModuleSensors
