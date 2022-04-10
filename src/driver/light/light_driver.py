import os
import sys
import time
from configparser import ConfigParser

sys.path.append(os.path.dirname((os.path.dirname(os.path.dirname(os.path.realpath(__file__))))))
from driver.driver_template import SensorHubModuleTemplate

# >>>>>>>>>> Fill in imports >>>>>>>>>>
from driver.light.TCS34725 import TCS34725
# <<<<<<<<<< Fill in imports <<<<<<<<<<


class LightModule(SensorHubModuleTemplate):
    # >>>>>>>>>> Fill in declarations >>>>>>>>>>
    SENSORS = ['RGB', 'Light1', 'Light2']
    SENSORS_COLS = {
        'RGB': ['Red', 'Green', 'Blue', 'IR Luminance', 'Ambient Luminance'],
        'Light1': ['Value'],
        'Light2': ['Value']
    }
    # Used for locks
    # I2C, SPI, or both
    SENSORS_INTERFACE = {
        'RGB': ['I2C'],
        'Light1': [],
        'Light2': []
    }
    OPTIONS = ['logging']
    # <<<<<<<<<< Fill in declarations <<<<<<<<<<

    def __init__(self, config_path, interface, **kwargs):
        super().__init__(config_path, interface, **kwargs)
        self.logger = kwargs['logger']
        self.logger.info('Init')
        # >>>>>>>>>> Fill in driver initializations >>>>>>>>>>
        self.driver = TCS34725(interface.i2c_bus)
        self.adc_read = interface.read_adc
        # <<<<<<<<<< Fill in driver initializations <<<<<<<<<<
        self.logger.info('Ready')

    def setup_config(self):
        # >>>>>>>>>> Fill in configuration setups >>>>>>>>>>
        self.fs = {
            'RGB': self.config['RGB Sensor'].getfloat('SamplingFrequency'),
            'Light1': self.config['Luminance Sensor 1'].getfloat('SamplingFrequency'),
            'Light2': self.config['Luminance Sensor 2'].getfloat('SamplingFrequency')
        }

        self.next_sched = {
            'RGB': time.time(),
            'Light1': time.time(),
            'Light2': time.time(),
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
        if sensor == 'RGB':
            red, green, blue, ir, luminance = self.driver.read()
            return {'_t': time.time(), 'Red': red, 'Green': green, 'Blue': blue, 'IR Luminance': ir, 'Ambient Luminance': luminance}
        elif sensor == 'Light1':
            return {'_t': time.time(), 'Value': self.adc_read(0)}
        elif sensor == 'Light2':
            return {'_t': time.time(), 'Value': self.adc_read(1)}
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
        time.sleep(max(0, min(list(self.next_sched.values())) - time.time()))
        return self.wait_for_next_sample()
