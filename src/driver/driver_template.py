# SensorHub Module Driver Template
# Note:
#       All drivers must inherit this class
import time
from configparser import ConfigParser


class SensorHubModuleTemplate:
    def __init__(self, config_path, interface):
        # TODO: Add lock
        print(f'I2C Bus: {interface.i2c_bus}')

        self.config = ConfigParser()
        # https://stackoverflow.com/questions/19359556/configparser-reads-capital-keys-and-make-them-lower-case
        self.config.optionxform = str  # Make config keys case sensitive
        self.config.read(config_path)

    def get_config(self, sensor_name=None, item_name=None):
        if sensor_name is None:
            return self.config
        if item_name is None:
            return self.config[sensor_name]
        else:
            return self.config[sensor_name][item_name]

    def read(self, sensor) -> str:
        return 'data string to be appended to the file accessed by user\n'

    def wait_for_next_sample(self) -> list:
        """
        Sleep some time calculated from config - sampling frequency, or wait for interrupt
        :return: List of sensors available for reading
        """
        time.sleep(0.2)
        return ['SensorName']
