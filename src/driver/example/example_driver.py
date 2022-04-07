import os
import sys
import time
from configparser import ConfigParser

sys.path.append(os.path.dirname((os.path.dirname(os.path.dirname(os.path.realpath(__file__))))))
from driver.driver_template import SensorHubModuleTemplate

# >>>>>>>>>> Fill in imports >>>>>>>>>>
from driver.example.ExampleLibrary import ExampleLibrary
# <<<<<<<<<< Fill in imports <<<<<<<<<<


class ExampleModule(SensorHubModuleTemplate):
    # >>>>>>>>>> Fill in declarations >>>>>>>>>>
    SENSORS = ['Sensor A', 'Sensor B']
    SENSORS_COLS = {
        'Sensor A': ['A-1', 'A-2'],
        'Sensor B': ['B-1']
    }
    # Used for locks
    # I2C, SPI, or both
    SENSORS_INTERFACE = {
        'Sensor A': ['I2C', 'SPI'],
        'Sensor B': ['SPI']
    }
    OPTIONS = ['logging']
    # <<<<<<<<<< Fill in declarations <<<<<<<<<<

    def __init__(self, config_path, interface, **kwargs):
        super().__init__(config_path, interface, **kwargs)
        self.logger = kwargs['logger']
        self.logger.info('Init')
        # >>>>>>>>>> Fill in driver initializations >>>>>>>>>>
        self.driver = ExampleLibrary()
        # <<<<<<<<<< Fill in driver initializations <<<<<<<<<<
        self.logger.info('Ready')

    def setup_config(self):
        # >>>>>>>>>> Fill in configuration setups >>>>>>>>>>
        self.fs = {
            'Sensor A': self.config['Sensor A'].getfloat('SamplingFrequency'),
            'Sensor B': self.config['Sensor B'].getfloat('SamplingFrequency')
        }

        self.next_sched = {
            'Sensor A': time.time(),
            'Sensor B': time.time()
        }
        # <<<<<<<<<< Fill in configuration setups <<<<<<<<<<

    # >>>>>>>>>> Fill in custom functions >>>>>>>>>>
    def _calc_next_sched(self, sensor):
        assert sensor in self.fs.keys()
        assert sensor in self.next_sched.keys()
        self.next_sched[sensor] = time.time() + (1 / self.fs[sensor])
    # <<<<<<<<<< Fill in custom functions <<<<<<<<<<

    def read(self, sensor):
        # >>>>>>>>>> Fill in reading values >>>>>>>>>>
        if sensor == 'Sensor A':
            rand1 = self.driver.read_a()
            rand2 = self.driver.read_b()
            return {'_t': time.time(), 'A-1': rand1, 'A-2': rand2}
        elif sensor == 'Sensor B':
            rand1 = self.driver.read_c()
            return {'_t': time.time(), 'B-1': rand1}
        # <<<<<<<<<< Fill in reading values <<<<<<<<<<
        else:
            raise ValueError(f'{sensor}: not implemented')

    def wait_for_next_sample(self):
        # Check if any sensor is due to be read
        for sensor in self.SENSORS:
            if self.next_sched[sensor] < time.time():
                self._calc_next_sched(sensor)
                return [sensor]
        
        # Wait until one of the sensor is due to be read
        time.sleep(min(list(self.next_sched.values())) - time.time())
        return self.wait_for_next_sample()
