import os
import sys
import time
import traceback

sys.path.append(os.path.dirname((os.path.dirname(os.path.dirname(os.path.realpath(__file__))))))
from driver.driver_template import SensorHubModuleTemplate

# >>>>>>>>>> Fill in imports >>>>>>>>>>
from driver.thermalcouple.MAX31855 import MAX31855
# <<<<<<<<<< Fill in imports <<<<<<<<<<


class ThermalcoupleModule(SensorHubModuleTemplate):
    # >>>>>>>>>> Fill in declarations >>>>>>>>>>
    SENSORS = ['thermalcouple']
    SENSORS_COLS = {
        'thermalcouple': ['rj', 'tc'],
    }
    SENSORS_INTERFACE = {
        'thermalcouple': ['SPI'],
    }
    OPTIONS = ['logging']
    # <<<<<<<<<< Fill in declarations <<<<<<<<<<

    def __init__(self, config_path, interface, **kwargs):
        self.logger = kwargs['logger']
        self.logger.info('Init')
        super().__init__(config_path, interface, **kwargs)

        # >>>>>>>>>> Fill in driver initializations >>>>>>>>>>
        pins = interface.spi_pins_bcm
        self.thermalcouple = MAX31855(pins['cs'], pins['sck'], pins['miso'], 'c')
        # <<<<<<<<<< Fill in driver initializations <<<<<<<<<<
        self.logger.info('Ready')

    def setup_config(self):
        # >>>>>>>>>> Fill in configuration setups >>>>>>>>>>
        self.fs = float(self.get_config('Thermalcouple', 'SamplingFrequency'))
        # <<<<<<<<<< Fill in configuration setups <<<<<<<<<<

    def read(self, sensor):
        # >>>>>>>>>> Fill in reading values >>>>>>>>>>
        if sensor == 'thermalcouple':
            rj = self.thermalcouple.get_rj()
            tc = self.thermalcouple.get()
            return {'_t': time.time(), 'rj': rj, 'tc': tc}
        # <<<<<<<<<< Fill in reading values <<<<<<<<<<
        else:
            return f'{sensor}: not implemented'

    def wait_for_next_sample(self):
        time.sleep(1 / self.fs)
        return self.SENSORS
