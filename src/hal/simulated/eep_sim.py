import random
import time


class EEPSimulated(object):
    def __init__(self):
        self.slots_taken = [True, False, False, False]
        self.module_names = {1: "Air Quality", 2: "", 3: "", 4: ""}
        self._update = self._sim_update()

    def _sim_update(self):
        last_time = time.time()
        while True:
            if time.time() - last_time > 5:
                last_time = time.time()
                self.slots_taken[1] = not self.slots_taken[1]
                if self.slots_taken[1]:
                    self.module_names[2] = random.sample(["Wind", "Multi-purpose Air Sensor"], k=1)[0]
                else:
                    self.module_names[2] = ""
            yield

    def get_status(self):
        next(self._update)
        return self.slots_taken, self.module_names
