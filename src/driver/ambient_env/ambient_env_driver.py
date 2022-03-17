import os
import sys
import time

sys.path.append(os.path.dirname((os.path.dirname(os.path.dirname(os.path.realpath(__file__))))))
from driver.driver_template import SensorHubModuleTemplate

### Fill in imports >>
from driver.ambient_env.AHT20 import AHT20
from driver.ambient_env.SPL06 import SPL06
### << Fill in imports

### Fill in declarations >>
AmbientEnvSensors = ['temp_hum', 'pressure']
AmbientEnvSensorsColumns = {
    'temp_hum': ['Temperature', 'Humidity'],
    'pressure': ['Pressure']
}
### << Fill in declarations

class AmbientEnvModule(SensorHubModuleTemplate):
    def __init__(self, config_path, interface):
        print('AmbientEnv init')
        super().__init__(config_path, interface)

        ### Fill in driver initializations >>
        self.temp_hum = AHT20(bus=interface.i2c_bus)
        self.pressure = SPL06(bus=interface.i2c_bus)
        ### << Fill in declarations

    def setup_config(self):
        ### Fill in configutation setups >>
        self.fs = float(self.get_config('Ambient Environment Sensor', 'SamplingFrequency'))
        ### << Fill in configutation setups

    def read(self, sensor):
        ### Fill in reading values >>
        if sensor == 'temp_hum':
            temperature = self.temp_hum.get_temperature()
            humidity = self.temp_hum.get_humidity()
            return {'_t': time.time(), 'Temperature': temperature, 'Humidity': humidity}
        elif sensor == 'pressure':
            return {'_t': time.time(), 'Pressure': self.pressure.get_pressure()}
        ### << Fill in reading values
        else:
            return f'{sensor}: not implemented'

    def wait_for_next_sample(self):
        time.sleep(1 / self.fs)
        return AmbientEnvSensors
