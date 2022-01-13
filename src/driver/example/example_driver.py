import os
import sys
import time
from configparser import ConfigParser

sys.path.append(os.path.dirname((os.path.dirname(os.path.dirname(os.path.realpath(__file__))))))
from driver.driver_template import SensorHubModuleTemplate

ExampleSensors = ['Sensor A', 'Sensor B']
ExampleSensorsProperties = {
    'Sensor A': ['A-1', 'A-2'],
    'Sensor B': ['B-1']
}

class ExampleModule(SensorHubModuleTemplate):
    def __init__(self, config_path, interface):
        super().__init__(config_path, interface)
        print('ExampleModule init')

    def setup_config(self):
        self.fs = {
            'Sensor A': self.config['Sensor A'].getfloat('SamplingFrequency'),
            'Sensor B': self.config['Sensor B'].getfloat('SamplingFrequency')
        }

        self.next_sched = {
            'Sensor A': time.time(),
            'Sensor B': time.time()
        }

    def _calc_next_sched(self, sensor):
        assert sensor in self.fs.keys()
        assert sensor in self.next_sched.keys()
        self.next_sched[sensor] = time.time() + (1 / self.fs[sensor])

    def read(self, sensor):
        if sensor == 'Sensor A':
            value_a = time.time() * 10 % 100
            value_b = time.time() % 10
            return {'_t': time.time(), 'A-1': value_a, 'A-2': value_b}
        elif sensor == 'Sensor B':
            value_a = 50 + time.time() * 10 % 100
            value_b = 5 + time.time() % 10
            return {'_t': time.time(), 'B-1': value_a}
        else:
            return f'{sensor}: not implemented'

    def wait_for_next_sample(self):
        for sensor in ExampleSensors:
            if self.next_sched[sensor] < time.time():
                self._calc_next_sched(sensor)
                return [sensor]
        return []
