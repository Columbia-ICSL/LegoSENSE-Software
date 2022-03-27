import os
import sys
import time

sys.path.append(os.path.dirname((os.path.dirname(os.path.dirname(os.path.realpath(__file__))))))
from driver.driver_template import SensorHubModuleTemplate

# >>>>>>>>>> Fill in imports >>>>>>>>>>
# pip install pimoroni-sgp30
from smbus2 import SMBus, i2c_msg
from sgp30 import SGP30
# <<<<<<<<<< Fill in imports <<<<<<<<<<


class IndoorAirQualityModule(SensorHubModuleTemplate):
    # >>>>>>>>>> Fill in declarations >>>>>>>>>>
    SENSORS = ["Indoor Air Quality"]
    SENSORS_COLS = {
        "Indoor Air Quality": ["CO2", "VOC"]
    }
    # <<<<<<<<<< Fill in declarations <<<<<<<<<<

    def __init__(self, config_path, interface):
        print('IndoorAirQualityModule init')
        super().__init__(config_path, interface)

        # >>>>>>>>>> Fill in driver initializations >>>>>>>>>>
        self.sgp30 = SGP30(i2c_dev=SMBus(interface.i2c_bus), i2c_msg=i2c_msg)
        self.sgp30.start_measurement(lambda: print("SGP30 warming up..."))  # Takes some time to warm up
        # <<<<<<<<<< Fill in driver initializations <<<<<<<<<<

    def setup_config(self):
        # >>>>>>>>>> Fill in configuration setups >>>>>>>>>>
        self.fs = float(self.get_config('Indoor Air Quality Sensor', 'SamplingFrequency'))
        # <<<<<<<<<< Fill in configuration setups <<<<<<<<<<

    def read(self, sensor):
        # >>>>>>>>>> Fill in reading values >>>>>>>>>>
        if sensor == 'Indoor Air Quality':
            result = self.sgp30.get_air_quality()
            return {'_t': time.time(), 'CO2': result.equivalent_co2, 'VOC': result.total_voc}
        # <<<<<<<<<< Fill in reading values <<<<<<<<<<
        else:
            return f'{sensor}: not implemented'

    def wait_for_next_sample(self):
        time.sleep(1 / self.fs)
        return self.SENSORS