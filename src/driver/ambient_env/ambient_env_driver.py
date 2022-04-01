import os
import sys
import time
import traceback

sys.path.append(os.path.dirname((os.path.dirname(os.path.dirname(os.path.realpath(__file__))))))
err_log_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'err.log')
from driver.driver_template import SensorHubModuleTemplate

# >>>>>>>>>> Fill in imports >>>>>>>>>>
from driver.ambient_env.AHT20 import AHT20
from driver.ambient_env.SPL06 import SPL06
# <<<<<<<<<< Fill in imports <<<<<<<<<<


class AmbientEnvModule(SensorHubModuleTemplate):
    # >>>>>>>>>> Fill in declarations >>>>>>>>>>
    SENSORS = ['temp_hum', 'pressure']
    SENSORS_COLS = {
        'temp_hum': ['Temperature', 'Humidity'],
        'pressure': ['Pressure']
    }
    SENSORS_INTERFACE = {
        'temp_hum': ['I2C'],
        'pressure': ['I2C']
    }
    OPTIONS = ['nolock', 'logging']
    # <<<<<<<<<< Fill in declarations <<<<<<<<<<

    def __init__(self, config_path, interface, **kwargs):
        self.lock = kwargs['lock']
        self.logger = kwargs['logger']
        self.logger.info('Init')
        super().__init__(config_path, interface, **kwargs)

        # >>>>>>>>>> Fill in driver initializations >>>>>>>>>>
        self.temp_hum = AHT20(lock=self.lock['I2C'], bus=interface.i2c_bus)
        self.pressure = SPL06(bus=interface.i2c_bus)
        # <<<<<<<<<< Fill in driver initializations <<<<<<<<<<
        self.logger.info('Ready')

    def setup_config(self):
        # >>>>>>>>>> Fill in configuration setups >>>>>>>>>>
        self.fs = float(self.get_config('Ambient Environment Sensor', 'SamplingFrequency'))
        # <<<<<<<<<< Fill in configuration setups <<<<<<<<<<

    def read(self, sensor):
        # >>>>>>>>>> Fill in reading values >>>>>>>>>>
        if sensor == 'temp_hum':
            temperature = self.temp_hum.get_temperature()
            humidity = self.temp_hum.get_humidity()
            return {'_t': time.time(), 'Temperature': temperature, 'Humidity': humidity}
        elif sensor == 'pressure':
            return {'_t': time.time(), 'Pressure': self.pressure.get_pressure()}
        # <<<<<<<<<< Fill in reading values <<<<<<<<<<
        else:
            return f'{sensor}: not implemented'

    def wait_for_next_sample(self):
        time.sleep(1 / self.fs)
        return self.SENSORS
