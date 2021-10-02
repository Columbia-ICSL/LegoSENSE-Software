import time
import datetime
from threading import Thread
from config import MODULES


class SensorHubModule(Thread):
    def __init__(self, module, sensors):
        assert isinstance(module, str)
        assert isinstance(sensors, list)

        assert len(sensors) == len(MODULES[module])
        self.module = module
        self.sensor = dict()
        for i in sensors:
            self.sensor[i] = f"Module {self.module}: {i}\n".encode()
        print(f"{self.module} init")

        Thread.__init__(self)
        self.start()

    def run(self):
        # TODO: Gracefully kill the thread
        while True:
            print(f'{self.module} working...')
            timestr = (datetime.datetime.now() + datetime.timedelta(hours=3)).strftime("[%H:%M:%S.%f]")

            for i in self.sensor.keys():
                hum = 10
                temp = 20
                self.sensor[i] += f'{timestr}\t{temp:.2f}\t{hum:.2f}\n'.encode()
            time.sleep(0.2)
