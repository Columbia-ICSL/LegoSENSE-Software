def get_i2c_bus(slot):
    if slot in ['slot1', 'slot2']:
        return 1
    elif slot in ['slot3', 'slot4']:
        return 6

class SensorHubInterface:
    def __init__(self, slot):
        self.slot = slot

    @property
    def i2c_bus(self):
        return get_i2c_bus(self.slot)