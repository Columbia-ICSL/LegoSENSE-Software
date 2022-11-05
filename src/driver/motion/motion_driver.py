import os
import sys
import time
from configparser import ConfigParser

sys.path.append(os.path.dirname((os.path.dirname(os.path.dirname(os.path.realpath(__file__))))))
from driver.driver_template import SensorHubModuleTemplate

# >>>>>>>>>> Fill in imports >>>>>>>>>>
from driver.motion.mpu6050 import mpu6050
# <<<<<<<<<< Fill in imports <<<<<<<<<<


class MotionModule(SensorHubModuleTemplate):
    # >>>>>>>>>> Fill in declarations >>>>>>>>>>
    SENSORS = ['IMU']
    SENSORS_COLS = {
        'IMU': ['AccX', 'AccY', 'AccZ', 'GyroX', 'GyroY', 'GyroZ']
    }
    # Used for locks
    # I2C, SPI, or both
    SENSORS_INTERFACE = {
        'IMU': ['I2C']
    }
    OPTIONS = ['logging']
    # <<<<<<<<<< Fill in declarations <<<<<<<<<<

    def __init__(self, config_path, interface, **kwargs):
        super().__init__(config_path, interface, **kwargs)
        self.logger = kwargs['logger']
        self.logger.info('Init')
        # >>>>>>>>>> Fill in driver initializations >>>>>>>>>>
        self.driver = mpu6050(address=0x68, bus=interface.i2c_bus)
        # <<<<<<<<<< Fill in driver initializations <<<<<<<<<<
        self.logger.info('Ready')

    def setup_config(self):
        # >>>>>>>>>> Fill in configuration setups >>>>>>>>>>
        self.fs = {
            'IMU': self.config['IMU'].getfloat('SamplingFrequency')
        }

        self.next_sched = {
            'IMU': time.time()
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
        if sensor == 'IMU':
            acc_data = self.driver.get_accel_data()
            gyro_data = self.driver.get_gyro_data()
            return {'_t': time.time(), 'AccX': acc_data['x'], 'AccY': acc_data['y'], 'AccZ': acc_data['z'], 'GyroX': gyro_data['x'], 'GyroY': gyro_data['y'], 'GyroZ': gyro_data['z']}
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
