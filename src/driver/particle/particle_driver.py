import os
import sys
import time

sys.path.append(os.path.dirname((os.path.dirname(os.path.dirname(os.path.realpath(__file__))))))
from driver.driver_template import SensorHubModuleTemplate

# >>>>>>>>>> Fill in imports >>>>>>>>>>
# pip install pms5003
from pms5003 import PMS5003
# <<<<<<<<<< Fill in imports <<<<<<<<<<


class ParticleModule(SensorHubModuleTemplate):
    # >>>>>>>>>> Fill in declarations >>>>>>>>>>
    SENSORS = ["Particle Matter"]
    SENSORS_COLS = {
        "Particle Matter": ["PM1.0_ultrafine","PM2.5_combustion_particles__organic_compounds__metals","PM10__dust__pollen__mould_spores","PM1.0_atoms_env","PM2.5_atoms_env","PM10_atoms_env","LT0.3um","LT0.5um","LT1.0um","LT2.5um","LT5.0um","LT10um"]
    }
    # <<<<<<<<<< Fill in declarations <<<<<<<<<<

    def __init__(self, config_path, interface):
        print('ParticleModule init')
        super().__init__(config_path, interface)

        # >>>>>>>>>> Fill in driver initializations >>>>>>>>>>
        self.pms5003 = PMS5003(
            device=interface.uart,
            baudrate=9600,
            pin_enable=interface.pin_rst,  # We did not connect enable
            pin_reset=interface.pin_rst
        )
        # <<<<<<<<<< Fill in driver initializations <<<<<<<<<<
        print('ParticleModule init done')

    def setup_config(self):
        # >>>>>>>>>> Fill in configuration setups >>>>>>>>>>
        self.fs = float(self.get_config('Particle Sensor', 'SamplingFrequency'))
        # <<<<<<<<<< Fill in configuration setups <<<<<<<<<<

    def read(self, sensor):
        # >>>>>>>>>> Fill in reading values >>>>>>>>>>
        if sensor == 'Particle Matter':
            data = self.pms5003.read()
            ret = dict(zip(
                ["PM1.0_ultrafine","PM2.5_combustion_particles__organic_compounds__metals","PM10__dust__pollen__mould_spores","PM1.0_atoms_env","PM2.5_atoms_env","PM10_atoms_env","LT0.3um","LT0.5um","LT1.0um","LT2.5um","LT5.0um","LT10um"],
                data.data[:-2]
            ))
            ret['_t'] = time.time()
            return ret
        # <<<<<<<<<< Fill in reading values <<<<<<<<<<
        else:
            return f'{sensor}: not implemented'

    def wait_for_next_sample(self):
        time.sleep(1 / self.fs)
        return self.SENSORS
