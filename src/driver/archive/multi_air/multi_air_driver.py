import os
import sys
import time

sys.path.append(os.path.dirname((os.path.dirname(os.path.dirname(os.path.realpath(__file__))))))
from driver.driver_template import SensorHubModuleTemplate

from archive.multi_air.hdc2080 import Pi_HDC2080

MultiAirModuleSensors = ['airQua', 'TempHum', 'CO2']
MultiAirModuleSensorsColumns = {
    'airQua': ['Air Quality'],
    'TempHum': ['Temperature', 'Humidity'],
    'CO2': ['CO2 Density']
}

class MultiAirModule(SensorHubModuleTemplate):
    def __init__(self, config_path, interface):
        print('MultiAirModule init')
        super().__init__(config_path, interface)

        self.temp_hum = Pi_HDC2080(twi=interface.i2c_bus)
        self.temp_hum.readHumidity()

    def setup_config(self):
        self.fs = float(self.get_config('Temperature Humidity', 'SamplingFrequency'))

    def read(self, sensor):
        if sensor == 'TempHum':
            tem = round(self.temp_hum.readTemperature(), 2)
            hum = round(self.temp_hum.readHumidity(), 2)
            # TODO: move this formatting into template
            return {'_t': time.time(), 'Temperature': tem, 'Humidity': hum}
        else:
            return f'{sensor}: not implemented'

    def wait_for_next_sample(self):
        time.sleep(1 / self.fs)
        return MultiAirModuleSensors
