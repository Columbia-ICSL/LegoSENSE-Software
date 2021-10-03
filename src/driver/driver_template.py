# SensorHub Module Driver Template
# Note:
#       All drivers must inherit this class

class SensorHubModuleTemplate:
    def __init__(self, config_path):
        # TODO: Add lock
        pass

    def read(self, sensor) -> str:
        return 'data string to be appended to the file accessed by user\n'
