import re
import importlib
import config
from worker import ModuleWorker, PlugAndPlayWorker, start_web_server


class SensorHubModuleManager:
    def __init__(self):
        self.installed_modules = config.INSTALLED_MODULES
        self.modules_worker = dict()
        self.util_worker = []
        self.start_workers()
        start_web_server(self)

    def __del__(self):
        self.stop_workers()

    def start_workers(self):
        for slot, module in self.installed_modules.items():
            if module != '':
                self.modules_worker[module] = ModuleWorker(module, slot)
        self.util_worker.append(PlugAndPlayWorker())

    def stop_workers(self):
        print('Stopping sensor workers....')
        for worker in self.modules_worker.values():
            worker.active = False
        for worker in self.modules_worker.values():
            worker.join()
        self.modules_worker = dict()
        print('Sensor workers stopped')

    def get_modules(self):
        installed_modules = list(self.modules_worker.keys())
        empty_slots = [slot for slot in list(self.installed_modules.keys()) if self.installed_modules[slot] == '']
        return installed_modules + empty_slots

    def get_sensors(self, module):
        return self.modules_worker[module].module_sensors if module in self.modules_worker.keys() else []

    def get_sensor_cols(self, module):
        return self.modules_worker[module].sensor_cols

    def get_modules_and_sensors(self):
        modules = []
        for slot_name, module_name in self.installed_modules.items():
            module = dict()
            if module_name != '':
                slot_number = re.findall(r'slot(\d+)', slot_name)
                assert len(slot_number) == 1, f'Unable to parse slot number from "{slot_name}"!'
                sensors = self.get_sensors(module_name)
                assert len(sensors) > 0, f'DriverError: Module "{module_name}" has empty list of sensors!'
                module['slot'] = int(slot_number[0])
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

        # Reload config
        importlib.reload(config)
        self.installed_modules = config.INSTALLED_MODULES

        self.start_workers()
        return {'ok': True, 'err_msg': ''}

    def module_start(self, module):
        return {'ok': True, 'mod_name': 'fake_module'}

    def module_stop(self, module):
        return {'ok': True, 'mod_name': 'fake_module'}

    def module_restart(self, module):
        return {'ok': True, 'mod_name': 'fake_module'}
