import re
import time
import importlib
import config
from worker import ModuleWorker, PlugAndPlayWorker, start_web_server
from log_util import get_logger
logger = get_logger('ModuleManager')

class SensorHubModuleManager:
    def __init__(self):
        logger.info("Init")
        self.modules_worker = dict()
        self.modules_detector = PlugAndPlayWorker(self.reload)
        time.sleep(2) # FIXME: change to pipe. Wait for EEPROM to refresh
        self.installed_modules = self.modules_detector.connected_modules
        logger.info(f'Slot allocation: {self.installed_modules}')
        self.start_workers()
        start_web_server(self)
        logger.info("Init Done")


    def __del__(self):
        self.stop_workers()

    def start_workers(self):
        for slot, module in self.installed_modules.items():
            if module != '':
                logger.debug(f"Init ModuleWorker for {module} at {slot}")
                self.modules_worker[module] = ModuleWorker(module, slot)

    def stop_workers(self):
        logger.info('Stopping sensor workers....')
        for worker in self.modules_worker.values():
            worker.active = False
        for worker in self.modules_worker.values():
            worker.join()
        self.modules_worker = dict()
        logger.info('Sensor workers stopped')

    def get_modules(self):
        installed_modules = list(self.modules_worker.keys())
        # empty_slots = [f'slot{slot}-empty' for slot in list(self.installed_modules.keys()) if self.installed_modules[slot] == '']
        return installed_modules

    def get_sensors(self, module):
        return self.modules_worker[module].module_sensors if module in self.modules_worker.keys() else []

    def get_sensor_cols(self, module):
        return self.modules_worker[module].sensor_cols

    def get_modules_and_sensors(self):
        modules = []
        for slot_name, module_name in self.installed_modules.items():
            module = dict()
            if module_name != '':
                sensors = self.get_sensors(module_name)
                assert len(sensors) > 0, f'DriverError: Module "{module_name}" has empty list of sensors!'
                module['slot'] = slot_name
                module['name'] = module_name
                module['sensors'] = zip(sensors, list(range(len(sensors))))
                modules.append(module)
        return modules

    def get_module_config(self, module):
        parsed = self.modules_worker[module].driver.get_config()
        return {section: dict(parsed.items(section)) for section in parsed.sections()}
        # TODO: have driver define each config's default, data type, UI type (slider, dropdown select, etc)

    def set_module_config(self, module, sensor, new_cfg):
        self.modules_worker[module].driver.update_config(sensor, new_cfg)
        # TODO: get status from driver
        return True

    def get_module_worker(self, module):
        return self.modules_worker[module]

    def get_sensor_filesize(self, module, sensor):
        return len(self.modules_worker[module].sensor[sensor])

    def get_sensor_data(self, module, sensor, offset, length):
        return self.modules_worker[module].sensor[sensor][offset: offset + length]

    def write_data(self, module, sensor, offset, buf):
        self.modules_worker[module].driver.write(buf)
        return len(buf)

    # ============ Callbacks from web server to control individual module ============
    # ================================================================================
    def reload(self):
        self.stop_workers()
        self.start_workers()
        return {'ok': True, 'err_msg': ''}

    def module_start(self, module):
        return {'ok': True, 'mod_name': 'fake_module'}

    def module_stop(self, module):
        return {'ok': True, 'mod_name': 'fake_module'}

    def module_restart(self, module):
        return {'ok': True, 'mod_name': 'fake_module'}
