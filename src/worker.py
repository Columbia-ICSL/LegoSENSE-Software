# Workers for SensorHub Background Process
import os
import time
import datetime
import importlib
from threading import Thread
from flask import Flask, make_response, render_template
from flask_sse import sse
# from gevent.pywsgi import WSGIServer
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
server.config['REDIS_URL'] = 'redis://localhost'
server.register_blueprint(sse, url_prefix='/stream')

manager = None


# TODO: Instead of copy these routes from SensorHub-dashboard submodule, import from it
@server.route("/")
def index_page():
    modules = manager.get_modules_and_sensors()
    return render_template('dashboard/main.html', segment="dashboard", modules=modules)


@server.route('/data')
def data():
    return render_template('data/main.html', segment="data")


# TODO: What if I have two same module?
@server.route('/module/<module_name>')
def module_details(module_name):
    module_info = {
        'name': module_name,
        'settings': {
            'Temperature & Humidity Sensor': {
                'Samples per second': 2
            },
            'CO2 Sensor': {
                'Samples per second': 1
            }
        }
    }
    return render_template('module/main.html', module=module_info)


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
    # Thread(target=lambda: WSGIServer(('0.0.0.0', WEB_SERVER_PORT), server).serve_forever()).start()


if __name__ == '__main__':
    import random
    import threading

    import numpy as np

    class _FakeModuleManager:
        fake_ok_response = {'ok': True, 'mod_name': 'fake_module'}
        slot1 = {
            'slot': 1,
            'name': 'Air Quality',
            'sensors': list(zip(['PM Sensor'], range(1)))
        }
        slot2 = {
            'slot': 2,
            'name': 'Wind',
            'sensors': list(zip(['Wind Speed Sensor'], range(1)))
        }
        slot3 = {
            'slot': 3,
            'name': 'Multi-purpose Air Sensor',
            'sensors': list(zip(['CO2 Sensor', 'Temperature & Humidity Sensor', 'Air Pressure Sensor'], range(3)))
        }
        def module_start(self, module): return self.fake_ok_response
        def module_stop(self, module): return self.fake_ok_response
        def module_restart(self, module): return self.fake_ok_response
        def get_modules_and_sensors(self): return [self.slot1, self.slot2, self.slot3]


    test_manager = _FakeModuleManager()

    def fake_data_worker():
        while True:
            data_from = random.sample(test_manager.get_modules_and_sensors(), k=1)[0]
            module = data_from['name']
            sensor = random.sample(data_from['sensors'], k=1)[0][0]
            t_window = list(np.linspace(time.time() - 1, time.time(), 10))
            data_window = list(map(lambda x: random.randint(0, 100), t_window))
            with server.app_context():
                destination = f'{module}.{sensor}'
                sse.publish({'time': t_window, 'data': data_window}, type=destination)
                print(f'Published to {destination}')
            time.sleep(0.1)

    threading.Thread(target=fake_data_worker, daemon=True).start()
    start_web_server(test_manager)
