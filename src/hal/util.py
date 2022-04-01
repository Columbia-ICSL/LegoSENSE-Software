import os
import sys
import contextlib
from threading import Lock

sys.path.append(os.path.dirname((os.path.dirname(os.path.realpath(__file__)))))
from log_util import get_logger
logger = get_logger('ResourceMngr')

_i2c_buses_lock = {
    1: Lock(),
    6: Lock()
    # 1: contextlib.nullcontext(),
    # 6: contextlib.nullcontext()
}

_spi_buses_lock = {
    0: Lock(),
    1: Lock()
    # 0: contextlib.nullcontext(),
    # 1: contextlib.nullcontext()
}

_locks = {
    'I2C': _i2c_buses_lock,
    'SPI': _spi_buses_lock
}

class ResourceManager:
    def __init__(self):
        pass

    def lock(self, interface, bus):
        global _locks
        if interface.upper() not in _locks.keys():
            logger.error(f'No lock found for interface: {interface}. Expected `I2C` or `SPI`!')
            return contextlib.nullcontext()
        if bus not in _locks[interface.upper()].keys():
            expected_keys = list(_locks[interface.upper()].keys())
            logger.error(f'No lock found for {interface}\'s bus {bus}. Expected {expected_keys}!')
            return contextlib.nullcontext()

        return _locks[interface.upper()][bus]
