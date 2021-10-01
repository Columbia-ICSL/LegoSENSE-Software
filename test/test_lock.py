import os
import sys
import time
from threading import Thread

SRC_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'src')
sys.path.append(SRC_DIR)

from seh import RM


class I2C_emu:
    def __init__(self):
        self.reader = 0

    def read(self):
        self.reader += 1
        assert self.reader == 1, 'Multiple readers! Check locks!'

    def fin(self):
        self.reader -= 1
        assert self.reader == 0, 'Multiple readers! Check locks!'


i2c = I2C_emu()


class M1(Thread):
    def __init__(self, use_lock):
        self.use_lock = use_lock
        Thread.__init__(self)
        self.start()

    def run(self):
        while True:
            if self.use_lock:
                RM.i2c_lock(1)
            print('M1 I2C OP')
            i2c.read()
            time.sleep(0.9)
            i2c.fin()
            if self.use_lock:
                RM.i2c_release(1)
            time.sleep(0.1)


class M2(Thread):
    def __init__(self, use_lock):
        self.use_lock = use_lock
        Thread.__init__(self)
        self.start()

    def run(self):
        while True:
            if self.use_lock:
                RM.i2c_lock(1)
            print('M2 I2C OP')
            i2c.read()
            time.sleep(1)
            i2c.fin()
            if self.use_lock:
                RM.i2c_release(1)
            time.sleep(0.1)


if __name__ == '__main__':
    use_lock = True
    m1 = M1(use_lock=use_lock)
    m2 = M2(use_lock=use_lock)
    while True:
        time.sleep(1)
