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
    SENSORS = ['temp_hum', 'pressure', 'wind']
    SENSORS_COLS = {
        'temp_hum': ['Temperature', 'Humidity'],
        'pressure': ['Pressure'],
        'wind': ['Value', 'Temperature']
    }
    SENSORS_INTERFACE = {
        'temp_hum': ['I2C'],
        'pressure': ['I2C'],
        'wind': []
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
        self.adc_read = interface.read_adc
        # <<<<<<<<<< Fill in driver initializations <<<<<<<<<<
        self.logger.info('Ready')

    def setup_config(self):
        # >>>>>>>>>> Fill in configuration setups >>>>>>>>>>
        self.fs = {
            'temp_hum': self.config['Temperature Humidity'].getfloat('SamplingFrequency'),
            'pressure': self.config['Pressure'].getfloat('SamplingFrequency'),
            'wind': self.config['Wind Speed'].getfloat('SamplingFrequency')
        }

        self.next_sched = {
            'temp_hum': time.time(),
            'pressure': time.time(),
            'wind': time.time()
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
        if sensor == 'temp_hum':
            temperature = self.temp_hum.get_temperature()
            humidity = self.temp_hum.get_humidity()
            return {'_t': time.time(), 'Temperature': temperature, 'Humidity': humidity}
        elif sensor == 'pressure':
            return {'_t': time.time(), 'Pressure': self.pressure.get_pressure()}
        elif sensor == 'wind':
            output = self.adc_read(0)
            tmp = self.adc_read(1)
            return {'_t': time.time(), 'Value': output, 'Temperature': tmp}
        # <<<<<<<<<< Fill in reading values <<<<<<<<<<
        else:
            return f'{sensor}: not implemented'

    def wait_for_next_sample(self):
        # Check if any sensor is due to be read
        for sensor in self.SENSORS:
            if self.next_sched[sensor] < time.time():
                self._calc_next_sched(sensor)
                return [sensor]
        
        # Wait until one of the sensor is due to be read
        time.sleep(min(list(self.next_sched.values())) - time.time())
        return self.wait_for_next_sample()

