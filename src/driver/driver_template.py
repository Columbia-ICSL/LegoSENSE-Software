# SensorHub Module Driver Template
# Note:
#       All drivers must inherit this class
import time


class SensorHubModuleTemplate:
    def __init__(self, config_path, interface):
        # TODO: Add lock
        print(f'I2C Bus: {interface.i2c_bus}')

    def read(self, sensor) -> str:
        return 'data string to be appended to the file accessed by user\n'

    def wait_for_next_sample(self) -> list:
        """
        Sleep some time calculated from config - sampling frequency, or wait for interrupt
        :return: List of sensors available for reading
        """
        time.sleep(0.2)
        return ['SensorName']
