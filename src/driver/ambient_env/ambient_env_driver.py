import os
import sys
import time

sys.path.append(os.path.dirname((os.path.dirname(os.path.dirname(os.path.realpath(__file__))))))
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
    # <<<<<<<<<< Fill in declarations <<<<<<<<<<

    def __init__(self, config_path, interface):
        print('AmbientEnv init')
        super().__init__(config_path, interface)

        # >>>>>>>>>> Fill in driver initializations >>>>>>>>>>
        self.temp_hum = AHT20(bus=interface.i2c_bus)
        self.pressure = SPL06(bus=interface.i2c_bus)
        # <<<<<<<<<< Fill in driver initializations <<<<<<<<<<

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
