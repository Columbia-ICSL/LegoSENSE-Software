# Workers for SensorHub Background Process
import os
import time
import json
import datetime
import importlib
import traceback
import subprocess
from threading import Thread
from contextlib import ExitStack

import redis
from flask import Flask, make_response, render_template, request, jsonify
from flask_sse import sse
# from gevent.pywsgi import WSGIServer
from config import WEB_SERVER_PORT
from hal.util import ResourceManager
from hal.interface import SensorHubInterface
from log_util import get_logger
import file_view

import platform
IS_RPI = platform.machine() == 'armv7l'

if IS_RPI:
    from hal.eeprom.eep_util import EEP
else:
    from hal.simulated.eep_sim import EEPSimulated as EEP

DRIVER_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'driver')
LOG_FOLDER = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'log')
if not os.path.exists(LOG_FOLDER):
    original_umask = os.umask(0)
    try:
        os.makedirs(LOG_FOLDER, 0o777)
    finally:
        os.umask(original_umask)

resource_manager = ResourceManager()

# --------------- Web server to handle requests from seh start/... ---------------
dashboard_root = os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'dashboard'), 'apps')
server = Flask(
    __name__,
    root_path=dashboard_root
)
server.config['REDIS_URL'] = 'redis://localhost'
server.register_blueprint(sse, url_prefix='/stream')
server_logger = get_logger('WebServer')
manager = None


# --------------- Use Redis to publish data to other applications, and receive notifications ---------------
redis_inst = redis.StrictRedis()

class DashboardUpdateReceiver(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.redis = redis.StrictRedis()
        self.pubsub = self.redis.pubsub()
        self.pubsub.psubscribe('dashboard_events')

    def run(self):
        for m in self.pubsub.listen():
            if 'pmessage' != m['type']:
                continue
            ch_name = m["channel"].decode('utf-8')
            ch_data = json.loads(m['data'].decode('utf-8'))
            if ch_name == 'dashboard_events':
                print(ch_data)
                with server.app_context():
                    destination = f'dashboard_events'
                    sse.publish(ch_data, type=destination)


class ModuleWorker(Thread):
    def __init__(self, module_name, slot):
        assert isinstance(module_name, str)
        self.logger = get_logger(f'Worker-M{slot}({module_name})')
        self.logger.info(f"Init")
        self.init_error = None

        # >>>>>>>>>>>> load driver >>>>>>>>>>>>
        self.module = module_name
        self.slot = slot
        module = importlib.import_module(f'driver.{module_name}')
        module_driver = module.SensorHubModule

        if module_driver.SENSORS is None:
            self.logger.error('DriverError: `SENSORS` is not declaired!')
            return
        if module_driver.SENSORS_COLS is None:
            self.logger.error('DriverError: `SENSORS_COLS` is not declaired!')
            return
        if module_driver.SENSORS_INTERFACE is None:
            self.logger.error('DriverError: `SENSORS_INTERFACE` is not declaired!')
            return

        self.module_sensors = module_driver.SENSORS
        self.sensor_fail = {i: False for i in self.module_sensors}  # For logging sensor back online after fail
        self.sensor_cols = module_driver.SENSORS_COLS
        self.sensor_interface = module_driver.SENSORS_INTERFACE
        self.module_opts = module_driver.OPTIONS
        self.fuse_data = dict()
        for i in self.module_sensors:
            self.fuse_data[i] = ('Time\t' + '\t'.join(self.sensor_cols[i]) + '\n').encode()

        self.interface = SensorHubInterface(f'slot{slot}')
        # <<<<<<<<<<<< load driver <<<<<<<<<<<<

        # >>>>>>>>>>>> driver Options >>>>>>>>>>>>
        additional_args = {}
        if 'nolock' in self.module_opts:
            additional_args['lock'] = {
                'I2C': resource_manager.lock('I2C', self.interface.i2c_bus),
                'SPI': resource_manager.lock('SPI', self.interface.spi_bus)
            }
        if 'logging' in self.module_opts:
            additional_args['logger'] = get_logger(f'Driver-M{slot}({module_name})')
        # <<<<<<<<<<<< driver Options <<<<<<<<<<<<

        for i in range(5):
            self.init_error = None
            try:
                self.driver = module_driver(
                    config_path=os.path.join(DRIVER_PATH, module_name, 'config.ini'),
                    interface=self.interface,
                    **additional_args
                )
                self.init_error = None
                break
            except:
                self.init_error = traceback.format_exc()
                self.logger.error(self.init_error)
                self.logger.error(f'Driver Init Failed. Wait 1 second before retrying...')
                time.sleep(1)
                continue
        
        if self.init_error is not None:
            fail_log_path = os.path.join(LOG_FOLDER,
                                        datetime.datetime.now().strftime(f"%y%m%d_%H%M%S_{module_name}_INIT_FAIL.csv"))
            with open(fail_log_path, 'w') as f:
                f.write(self.init_error)
            self.logger.error('Too much failed attempts to initialize driver. Daughterboard ignored.')
            return

        # >>>>>>>>>>>> prepare csv log >>>>>>>>>>>>
        self.csv_log_path = os.path.join(LOG_FOLDER,
                                         datetime.datetime.now().strftime(f"%y%m%d_%H%M%S_{module_name}.csv"))
        log_header = ["Epoch Time"]
        self.log_index = {}
        self.total_log_cols = 1
        for sensor, cols in self.sensor_cols.items():
            self.log_index[sensor] = dict(zip(cols, list(range(self.total_log_cols, self.total_log_cols + len(cols)))))
            self.total_log_cols += len(cols)
            log_header.extend([f'{sensor}_{i}' for i in cols])
        self.write_csv_from_list(log_header)
        # <<<<<<<<<<<< prepare csv log <<<<<<<<<<<<

        # >>>>>>>>>>>> start driver >>>>>>>>>>>>
        self.active = True
        Thread.__init__(self)
        self.start()
        # <<<<<<<<<<<< start driver <<<<<<<<<<<<

    def write_csv_from_list(self, data):
        assert isinstance(data, list)
        assert all([isinstance(i, str) for i in data])
        with open(self.csv_log_path, 'a') as f:
            out_data = ','.join(data)
            out_data += '\n'
            f.write(out_data)

    def format_log(self, sensor, data):
        # time_str = (datetime.datetime.now() + datetime.timedelta(hours=3)).strftime("[%H:%M:%S.%f]")

        if isinstance(data, str):
            t = str(time.time())
            return (t + '\t' + data + '\n').encode()
        elif isinstance(data, dict):
            for i in data.keys():
                if i != '_t':
                    if i not in self.sensor_cols[sensor]:
                        self.logger.error(f'DriverError: Sensor column {i} not found in SENSORS_COLS!'
                                          f'Ignored {i}')
                        del data[i]

            ret = str(data['_t'])
            for col in self.sensor_cols[sensor]:
                if col in data.keys():
                    ret += ('\t' + str(data[col]))
                else:
                    ret += '\t 0'  # Data not available
            return (ret + '\n').encode()
        else:
            self.logger.error(f'DriverError: Invalid read_data: {data}')

    def handle_data(self, sensor, data):
        self.save_log(sensor, data)
        redis_inst.publish(f'data-{sensor}', json.dumps(data).encode('utf-8'))
        with server.app_context():
            t = data['_t']
            del data['_t']
            for col, value in data.items():
                destination = f'{self.module}.{sensor}.{col}'
                sse.publish({'time': [t], 'data': [value]}, type=destination)
                # print(f'Published to {destination}')

    def save_log(self, sensor, data):
        log_cols = ["" for i in range(self.total_log_cols)]
        log_cols[0] = str(data['_t'])
        for col, col_data in data.items():
            if col == '_t':
                continue
            idx = self.log_index[sensor][col]
            log_cols[idx] = str(col_data)
        self.write_csv_from_list(log_cols)

    def run(self):
        while self.active:
            # print(f'{self.module} working...')
            try:
                available_sensors = self.driver.wait_for_next_sample()
                assert isinstance(available_sensors, list), \
                f'[{self.module}] DriverError: wait_for_next_sample must return list!'
            except:
                    self.logger.error(traceback.format_exc())
                    self.logger.error(f'wait_for_next_sample Failed. Wait 1 second before retrying...')
                    time.sleep(1)
                    continue
            for i in available_sensors:
                err = None
                if 'nolock' not in self.module_opts and len(self.sensor_interface[i]) != 0:
                    # Requires lock
                    with ExitStack() as context_mngr_stack:
                        # Locking for critical section
                        for sensor_interface in self.sensor_interface[i]:
                            lock = resource_manager.lock(sensor_interface, self.interface.from_str(sensor_interface))
                            # self.logger.debug(f'Locking {sensor_interface}')
                            context_mngr_stack.enter_context(lock)
                        # self.logger.debug(f'Lock acquired')
                        # <--------- Actual sensor read -- critical section --------->
                        try:
                            read_data = self.driver.read(i)
                        except:
                            err = traceback.format_exc()
                        # <------------------ end critical section ------------------>
                else:
                    try:
                        read_data = self.driver.read(i)
                    except:
                        err = traceback.format_exc()
                if err is None:
                    self.fuse_data[i] += self.format_log(i, read_data)
                    if isinstance(read_data, dict):
                        self.handle_data(i, read_data)
                    if self.sensor_fail[i]:
                        self.logger.info(f'[{i}] is now back online')
                        self.sensor_fail[i] = False
                else:
                    self.logger.error(err)
                    self.logger.error(f'[{i}] Failed. Wait 1 second before retrying...')
                    self.sensor_fail[i] = True
                    time.sleep(1)
        # Call driver's function to gracefully terminate
        self.driver.shutdown()
        self.logger.info(f'Terminated')


class PlugAndPlayWorker(Thread):
    def __init__(self, on_update_cb=None):
        self.logger = get_logger('PnP')
        self.logger.info('Init')
        self.eep = EEP(lock=resource_manager.lock('I2C', 1))
        self.connected_modules = {}
        self.on_update_cb = on_update_cb
        self.active = True
        Thread.__init__(self)
        self.start()

    def run(self):
        time.sleep(0.1)  # FIXME: change to pipe. Wait for EEPROM to refresh
        while True:
            _, self.connected_modules = self.eep.get_status()
            if all([len(i) == 0 for i in self.connected_modules.values()]):
                self.logger.error(f'No module detected... Retrying in 1 second')
                time.sleep(1)
            else:
                self.logger.info(f'Ready')
                break
        last_connected_modules = self.connected_modules.copy()
        while self.active:
            time.sleep(0.5)
            _, self.connected_modules = self.eep.get_status()
            if self.connected_modules != last_connected_modules:
                self.logger.debug(f'Module update! {last_connected_modules} -> {self.connected_modules}')
                if self.on_update_cb is not None:
                    self.on_update_cb()
                with server.app_context():
                    destination = f'dashboard_events'
                    sse.publish({
                        'type': 'module_list_changed',
                        'action': ['alert_then_refresh'],
                        'alert': 'Refreshing module list...',
                    }, type=destination)
                    # print(f'Published to {destination}')
                last_connected_modules = self.connected_modules.copy()


# TODO: Instead of copy these routes from SensorHub-dashboard submodule, import from it
@server.route("/get_slots")
def get_slots():
    modules = manager.installed_modules
    return jsonify(modules)


@server.route("/")
def index_page():
    modules = manager.get_modules_and_sensors()
    return render_template('dashboard/main.html', segment="dashboard", modules=modules)


@server.route("/shutdown")
def shutdown():
    subprocess.Popen("sleep 5 && /sbin/shutdown -h now", shell=True)
    return render_template('dashboard/message.html', segment="dashboard", title='Shutdown', message='System shutting down now... Please wait for 1 miunte before unplugging the cable.')


@server.route("/reboot")
def reboot():
    subprocess.Popen("sleep 5 && /sbin/reboot now", shell=True)
    return render_template('dashboard/message.html', segment="dashboard", title='Reboot', message='System rebooting now... Please allow up to 5 minutes for the system to connect to the Internet and go back up.')


# File explorer at /data
file_view.install(server)


# TODO: What if I have two same module?
@server.route('/module/<module_name>')
def module_details(module_name):
    module_info = {
        'name': module_name,
        'settings': manager.get_module_config(module_name),
        'sensors': manager.get_sensors(module_name),
        'sensor_cols': manager.get_sensor_cols(module_name)
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


@server.route('/update_settings', methods=['POST'])
def update_settings():
    server_logger.info('POST /update_settings')
    module = request.headers['Module-Name']
    sensor = request.headers['Sensor-Name']
    new_config = request.json
    manager.set_module_config(module, sensor, new_config)
    return jsonify({'status': 'OK', 'msg': f'{sensor} configurations saved'})


def start_web_server(module_manager):
    global manager
    manager = module_manager
    Thread(target=lambda: server.run(host='0.0.0.0', port=WEB_SERVER_PORT, debug=True, use_reloader=False)).start()
    # Thread(target=lambda: WSGIServer(('0.0.0.0', WEB_SERVER_PORT), server).serve_forever()).start()
    DashboardUpdateReceiver().start()

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
        fake_slots = {'Air Quality': slot1, 'Wind': slot2, 'Multi-purpose Air Sensor': slot3}
        def module_start(self, module): return self.fake_ok_response
        def module_stop(self, module): return self.fake_ok_response
        def module_restart(self, module): return self.fake_ok_response
        def get_modules_and_sensors(self): return [self.slot1, self.slot2, self.slot3]

        def get_module_config(self, module):
            assert module in ['Air Quality', 'Wind', 'Multi-purpose Air Sensor']
            fake_cfg = dict()
            for sensor, idx in self.fake_slots[module]['sensors']:
                fake_cfg[sensor] = {f'{sensor}ConfigKey': '1'}
            return fake_cfg

        def get_sensors(self, module):
            assert module in ['Air Quality', 'Wind', 'Multi-purpose Air Sensor']
            return [sensor for sensor, idx in self.fake_slots[module]['sensors']]

        def get_sensor_cols(self, module):
            assert module in ['Air Quality', 'Wind', 'Multi-purpose Air Sensor']
            sensor_cols = {
                'Air Quality': {'PM Sensor': ['PM Sensor']},
                'Wind': {'Wind Speed Sensor': ['Wind Speed Sensor']},
                'Multi-purpose Air Sensor': {
                    'CO2 Sensor': ['CO2 Sensor'],
                    'Temperature & Humidity Sensor': ['Temperature & Humidity Sensor'],
                    'Air Pressure Sensor': ['Air Pressure Sensor']
                }
            }
            return sensor_cols[module]

    test_manager = _FakeModuleManager()

    def fake_data_worker():
        while True:
            data_from = random.sample(test_manager.get_modules_and_sensors(), k=1)[0]
            module = data_from['name']
            sensor = random.sample(data_from['sensors'], k=1)[0][0]
            t_window = list(np.linspace(time.time() - 1, time.time(), 10))
            data_window = list(map(lambda x: random.randint(0, 100), t_window))
            with server.app_context():
                destination = f'{module}.{sensor}.{sensor}'
                sse.publish({'time': t_window, 'data': data_window}, type=destination)
                # print(f'Published to {destination}')
            time.sleep(0.1)

    threading.Thread(target=fake_data_worker, daemon=True).start()
    PlugAndPlayWorker()
    start_web_server(test_manager)
