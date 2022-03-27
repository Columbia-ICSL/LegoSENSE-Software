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
    # <<<<<<<<<< Fill in declarations <<<<<<<<<<

    def __init__(self, config_path, interface):
        print('AmbientEnv init')
        super().__init__(config_path, interface)

        # >>>>>>>>>> Fill in driver initializations >>>>>>>>>>
        self.temp_hum = AHT20(bus=interface.i2c_bus)
        self.pressure = SPL06(bus=interface.i2c_bus)
        # <<<<<<<<<< Fill in driver initializations <<<<<<<<<<
        print('AmbientEnv init done')

    def setup_config(self):
        # >>>>>>>>>> Fill in configuration setups >>>>>>>>>>
        self.fs = float(self.get_config('Ambient Environment Sensor', 'SamplingFrequency'))
        # <<<<<<<<<< Fill in configuration setups <<<<<<<<<<

    def read(self, sensor):
        # >>>>>>>>>> Fill in reading values >>>>>>>>>>
        if sensor == 'temp_hum':
            try:
                temperature = self.temp_hum.get_temperature()
                humidity = self.temp_hum.get_humidity()
                return {'_t': time.time(), 'Temperature': temperature, 'Humidity': humidity}
            except:
                with open(err_log_path, 'a') as f:
                    f.write(str(time.time()) + '\n' + traceback.format_exc() + '\n')
                traceback.print_exc()
                print("Waiting 2 sec before continuing")
                time.sleep(2)
                return {'_t': time.time(), 'Temperature': -1, 'Humidity': -1}
        elif sensor == 'pressure':
            try:
                return {'_t': time.time(), 'Pressure': self.pressure.get_pressure()}
            except:
                with open(err_log_path, 'a') as f:
                    f.write(str(time.time()) + '\n' + traceback.format_exc() + '\n')
                traceback.print_exc()
                print("Waiting 2 sec before continuing")
                time.sleep(2)
                return {'_t': time.time(), 'Pressure': -1}
        # <<<<<<<<<< Fill in reading values <<<<<<<<<<
        else:
            return f'{sensor}: not implemented'

    def wait_for_next_sample(self):
        time.sleep(1 / self.fs)
        return self.SENSORS
