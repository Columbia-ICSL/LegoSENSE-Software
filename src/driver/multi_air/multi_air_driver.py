import os
import sys

sys.path.append(os.path.dirname((os.path.dirname(os.path.dirname(os.path.realpath(__file__))))))
from driver.driver_template import SensorHubModuleTemplate


class MultiAirModule(SensorHubModuleTemplate):
    def __init__(self, config_path):
        print('MultiAirModule')
        super().__init__(config_path)

    def read(self, sensor):
        return f'{sensor} 10 10\n'
