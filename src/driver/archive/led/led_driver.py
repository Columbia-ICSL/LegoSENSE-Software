import os
import sys
import time
from configparser import ConfigParser

sys.path.append(os.path.dirname((os.path.dirname(os.path.dirname(os.path.realpath(__file__))))))
from driver.driver_template import SensorHubModuleTemplate

LEDModuleSensors = ['led1']


class LEDModule(SensorHubModuleTemplate):
    def __init__(self, config_path, interface):
        print('LEDModule init')
        super().__init__(config_path, interface)
        import RPi.GPIO as GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(13, GPIO.OUT)
        self.pwm_test = GPIO.PWM(13, 1000)

    def read(self, sensor):
        pass
    
    def write(self, data):
        duty = int(data.decode())
        print(duty)
        self.pwm_test.start(duty)


    def wait_for_next_sample(self):
        time.sleep(1)
        # No sensor to read
        return []
