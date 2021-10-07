# Workers for SensorHub Background Process
import os
import time
import datetime
import importlib
from threading import Thread
from flask import Flask, make_response

from config import WEB_SERVER_PORT

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

        # TODO: Pass in slot
        self.driver = module_driver(os.path.join(DRIVER_PATH, module_name, 'config.json'))

        self.active = True
        Thread.__init__(self)
        self.start()

    def run(self):
        while self.active:
            # print(f'{self.module} working...')
            timestr = (datetime.datetime.now() + datetime.timedelta(hours=3)).strftime("[%H:%M:%S.%f]")
            available_sensors = self.driver.wait_for_next_sample()
            for i in available_sensors:
                self.sensor[i] += (timestr + '\t' + self.driver.read(i)).encode()
        # TODO: call driver's function to gracefully terminate
        print(f'{self.module} at {self.slot} terminated')


# --------------- Web server to handle requests from seh start/... ---------------
server = Flask(__name__)
manager = None


@server.route("/")
def index_page():
    # TODO: Some system statistics?
    return make_response('SensorHub Running!')


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
