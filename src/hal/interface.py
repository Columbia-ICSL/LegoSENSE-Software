def get_i2c_bus(slot):
    if slot in ['slot1', 'slot2']:
        return 1
    elif slot in ['slot3', 'slot4']:
        return 6
    else:
        raise RuntimeError(f'Invalid slot {slot}!')

def get_uart(slot):
    if slot == 'slot1':
        # GPIO 14, 15 -- ALT0 -- UART0
        return '/dev/ttyS0'
    elif slot == 'slot2':
        # GPIO 0, 1 -- ALT4 -- UART2
        return '/dev/ttyAMA1'
    elif slot == 'slot3':
        # GPIO 4, 5 -- ALT4 -- UART3
        return '/dev/ttyAMA2'
    elif slot == 'slot4':
        # GPIO 12, 13 -- ALT4 -- UAR5
        return '/dev/ttyAMA3'


class SensorHubInterface:
    def __init__(self, slot):
        self.slot = slot

    @property
    def i2c_bus(self):
        return get_i2c_bus(self.slot)

    @property
    def uart(self):
        return get_uart(self.slot)
