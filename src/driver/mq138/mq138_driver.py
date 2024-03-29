import os
import sys
import time

sys.path.append(os.path.dirname((os.path.dirname(os.path.dirname(os.path.realpath(__file__))))))
from driver.driver_template import SensorHubModuleTemplate

# >>>>>>>>>> Fill in imports >>>>>>>>>>

# <<<<<<<<<< Fill in imports <<<<<<<<<<


class MQ138Module(SensorHubModuleTemplate):
    # >>>>>>>>>> Fill in declarations >>>>>>>>>>
    SENSORS = ['MQ138']
    SENSORS_COLS = {
        'MQ138': ['Reading']
    }
    SENSORS_INTERFACE = {
        'MQ138': []
    }
    # <<<<<<<<<< Fill in declarations <<<<<<<<<<

    def __init__(self, config_path, interface):
        print('MQ138 init')
        super().__init__(config_path, interface)

        # >>>>>>>>>> Fill in driver initializations >>>>>>>>>>
        self.adc_read_func = interface.read_adc
        # <<<<<<<<<< Fill in driver initializations <<<<<<<<<<
        print('MQ138 init done')

    def setup_config(self):
        # >>>>>>>>>> Fill in configuration setups >>>>>>>>>>
        self.fs = float(self.get_config('Gas Sensor', 'SamplingFrequency'))
        # <<<<<<<<<< Fill in configuration setups <<<<<<<<<<

    def read(self, sensor):
        # >>>>>>>>>> Fill in reading values >>>>>>>>>>
        if sensor == 'MQ138':
            return {'_t': time.time(), 'Reading': self.adc_read_func(channel=0)}
        # <<<<<<<<<< Fill in reading values <<<<<<<<<<
        else:
            return f'{sensor}: not implemented'

    def wait_for_next_sample(self):
        time.sleep(1 / self.fs)
        return self.SENSORS
