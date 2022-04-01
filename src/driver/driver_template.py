# SensorHub Module Driver Template
# Note:
#       All drivers must inherit this class
import time
from configparser import ConfigParser


class SensorHubModuleTemplate:
    SENSORS = None
    SENSORS_COLS = None
    SENSORS_INTERFACE = None
    OPTIONS = []

    def __init__(self, config_path, interface, **kwargs):
        self.config_path = config_path
        self.config = ConfigParser()
        # https://stackoverflow.com/questions/19359556/configparser-reads-capital-keys-and-make-them-lower-case
        self.config.optionxform = str  # Make config keys case sensitive
        self.config.read(config_path)
        self.setup_config()

    def get_config(self, sensor_name=None, item_name=None):
        if sensor_name is None:
            return self.config
        if item_name is None:
            return self.config[sensor_name]
        else:
            return self.config[sensor_name][item_name]

    def update_config(self, sensor_name, update_dict):
        for key, new_val in update_dict.items():
            self.config.set(sensor_name, key, new_val)
        with open(self.config_path, 'w') as configfile:
            self.config.write(configfile)

        self.setup_config()

    def setup_config(self):
        raise NotImplementedError

    def read(self, sensor) -> str:
        return 'data string to be appended to the file accessed by user\n'

    def wait_for_next_sample(self) -> list:
        """
        Sleep some time calculated from config - sampling frequency, or wait for interrupt
        :return: List of sensors available for reading
        """
        time.sleep(0.2)
        return ['SensorName']
