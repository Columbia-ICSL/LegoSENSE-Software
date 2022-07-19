import os
import sys
import time

sys.path.append(os.path.dirname((os.path.dirname(os.path.dirname(os.path.realpath(__file__))))))
from driver.driver_template import SensorHubModuleTemplate

# >>>>>>>>>> Fill in imports >>>>>>>>>>
import VL53L1X
# <<<<<<<<<< Fill in imports <<<<<<<<<<


class HumanActivityModule(SensorHubModuleTemplate):
    # >>>>>>>>>> Fill in declarations >>>>>>>>>>
    SENSORS = ['Microphone', 'Distance']
    SENSORS_COLS = {
        'Microphone': ['Microphone'],
        'Distance': ['Distance']
    }
    SENSORS_INTERFACE = {
        'Microphone': [],
        'Distance': ['I2C']
    }
    # <<<<<<<<<< Fill in declarations <<<<<<<<<<

    def __init__(self, config_path, interface, **kwargs):
        super().__init__(config_path, interface, **kwargs)

        # >>>>>>>>>> Fill in driver initializations >>>>>>>>>>
        self.adc_read_func = interface.read_adc
        self.tof = VL53L1X.VL53L1X(i2c_bus=interface.i2c_bus, i2c_address=0x29)
        self.tof.open()
        self.tof.set_timing(66000, 70)
        self.tof.start_ranging(0)   # Start ranging
                                    # 0 = Unchanged
                                    # 1 = Short Range
                                    # 2 = Medium Range
                                    # 3 = Long Range
        self.last_tof = 0
        # <<<<<<<<<< Fill in driver initializations <<<<<<<<<<

    def setup_config(self):
        # >>>>>>>>>> Fill in configuration setups >>>>>>>>>>
        self.fs = {
            'Microphone': self.config['Microphone'].getfloat('SamplingFrequency'),
            'Distance': self.config['Distance'].getfloat('SamplingFrequency')
        }
        self.next_sched = {
            'Microphone': time.time(),
            'Distance': time.time()
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
        if sensor == 'Microphone':
            return {'_t': time.time(), 'Microphone': self.adc_read_func(channel=0)}
        elif sensor == 'Distance':
            distance = self.tof.get_distance()
            if distance == 0:
                distance = self.last_tof
            else:
                self.last_tof = distance
            return {'_t': time.time(), 'Distance': distance}
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
        time.sleep(max(0, min(list(self.next_sched.values())) - time.time()))
        return self.wait_for_next_sample()

    def shutdown(self):
        self.tof.stop_ranging()
