from threading import Lock


class ResourceManager:
    def __init__(self):
        self.i2c_buses_lock = {
            1: Lock(),
            6: Lock()
        }
        self.spi_buses_lock = {
            0: Lock(),
            1: Lock()
        }

    def i2c_lock(self, bus):
        self.i2c_buses_lock[bus].acquire(blocking=True, timeout=-1)

    def i2c_release(self, bus):
        self.i2c_buses_lock[bus].release()

    def spi_lock(self, bus):
        self.spi_buses_lock[bus].acquire(blocking=True, timeout=-1)

    def spi_release(self, bus):
        self.spi_buses_lock[bus].release()
