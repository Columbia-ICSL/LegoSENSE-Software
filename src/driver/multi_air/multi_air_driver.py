import os
import sys
import time

sys.path.append(os.path.dirname((os.path.dirname(os.path.dirname(os.path.realpath(__file__))))))
from driver.driver_template import SensorHubModuleTemplate

MultiAirModuleSensors = ['airQua', 'TempHum', 'CO2']


class MultiAirModule(SensorHubModuleTemplate):
    def __init__(self, config_path):
        print('MultiAirModule init')
        super().__init__(config_path)

    def read(self, sensor):
        if sensor == 'TempHum':
            return f'10\t10\n'
        else:
            return f'{sensor}: not implemented'

    def wait_for_next_sample(self):
        time.sleep(0.2)
        return MultiAirModuleSensors
