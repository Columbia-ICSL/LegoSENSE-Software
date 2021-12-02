# Workers for SensorHub Background Process
import os
import time
import datetime
import importlib
from threading import Thread
from flask import Flask, make_response, render_template

from config import WEB_SERVER_PORT
from hal.interface import SensorHubInterface

DRIVER_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'driver')


class ModuleWorker(Thread):
    def __init__(self, module_name, slot):
        assert isinstance(module_name, str)
        print(f"{module_name} init at {slot}")

        self.module = module_name
        self.slot = slot
        module = importlib.import_module(f'driver.{module_name}')
        module_driver = module.SensorHubModule

        self.module_sensors = module.SENSORS
        self.sensor = dict()
        for i in self.module_sensors:
            self.sensor[i] = f"Module {self.module}: {i}\n".encode()

        self.interface = SensorHubInterface(slot)
        self.driver = module_driver(
            config_path=os.path.join(DRIVER_PATH, module_name, 'config.ini'),
            interface=self.interface
            )

        self.active = True
        Thread.__init__(self)
        self.start()

    def run(self):
        while self.active:
            # print(f'{self.module} working...')
            timestr = (datetime.datetime.now() + datetime.timedelta(hours=3)).strftime("[%H:%M:%S.%f]")
            available_sensors = self.driver.wait_for_next_sample()
            assert isinstance(available_sensors, list), \
                f'[{self.module}] DriverError: wait_for_next_sample must return list!'
            for i in available_sensors:
                self.sensor[i] += (timestr + '\t' + self.driver.read(i)).encode()
        # TODO: call driver's function to gracefully terminate
        print(f'{self.module} at {self.slot} terminated')


# --------------- Web server to handle requests from seh start/... ---------------
dashboard_root = os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'dashboard'), 'apps')
server = Flask(
    __name__,
    root_path=dashboard_root
)
manager = None


# TODO: Instead of copy these routes from SensorHub-dashboard submodule, import from it
@server.route("/")
def index_page():
    slot1 = {
        'slot': 1,
        'name': 'Air Quality',
        'sensors': zip(['PM Sensor'], range(1))
    }
    slot2 = {
        'slot': 2,
        'name': 'Wind',
        'sensors': zip(['Wind Speed Sensor'], range(1))
    }
    slot3 = {
        'slot': 3,
        'name': 'Multi-purpose Air Sensor',
        'sensors': zip(['CO2 Sensor', 'Temperature & Humidity Sensor', 'Air Pressure Sensor'], range(3))
    }
    return render_template('dashboard/main.html', segment="dashboard", modules=[slot1, slot2, slot3])


@server.route('/data')
def data():
    return render_template('data/main.html', segment="data")


@server.route('/setting/<module_name>')
def sensor_setting(module_name):
    module_info = {
        'name': module_name,
        'settings': {
            'Temperature Humidity': {
                'Samples per second': 2
            },
            'CO2': {
                'Samples per second': 1
            }
        }
    }
    return render_template('setting/main.html', module=module_info)


@server.route('/start/<string:text>', methods=['POST'])
def seh_start(text):
    response = manager.module_start(text)
    if response['ok']:
        return make_response('RUNNING: /dev/seh/{mod_name}'.format(mod_name=response['mod_name']))
    else:
        return make_response(response['err_msg']), 500


@server.route('/stop/<string:text>', methods=['POST'])
def seh_stop(text):
    response = manager.module_stop(text)
    if response['ok']:
        return make_response('STOPPED: /dev/seh/{mod_name}'.format(mod_name=response['mod_name']))
    else:
        return make_response(response['err_msg']), 500


@server.route('/restart/<string:text>', methods=['POST'])
def seh_restart(text):
    response = manager.module_restart(text)
    if response['ok']:
        return make_response('RESTARTED: /dev/seh/{mod_name}'.format(mod_name=response['mod_name']))
    else:
        return make_response(response['err_msg']), 500


@server.route('/reload', methods=['POST'])
def seh_reload_system():
    response = manager.reload()
    if response['ok']:
        return make_response('SensorHub service restarted')
    else:
        return make_response(response['err_msg']), 500


def start_web_server(module_manager):
    global manager
    manager = module_manager
    Thread(target=lambda: server.run(host='0.0.0.0', port=WEB_SERVER_PORT, debug=True, use_reloader=False)).start()


if __name__ == '__main__':
    class _FakeModuleManager:
        fake_ok_response = {'ok': True, 'mod_name': 'fake_module'}
        def module_start(self, module): return self.fake_ok_response
        def module_stop(self, module): return self.fake_ok_response
        def module_restart(self, module): return self.fake_ok_response

    start_web_server(_FakeModuleManager())
