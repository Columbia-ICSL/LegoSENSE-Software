import time
import datetime
from threading import Thread
from flask import Flask, make_response
from config import MODULES, WEB_SERVER_PORT


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
            # print(f'{self.module} working...')
            timestr = (datetime.datetime.now() + datetime.timedelta(hours=3)).strftime("[%H:%M:%S.%f]")

            for i in self.sensor.keys():
                hum = 10
                temp = 20
                self.sensor[i] += f'{timestr}\t{temp:.2f}\t{hum:.2f}\n'.encode()
            time.sleep(0.2)


# --------------- Web server to handle requests from seh start/... ---------------
server = Flask(__name__)


@server.route("/")
def index_page():
    # TODO: Some system statistics?
    return make_response('SensorHub Running!')


@server.route('/start/<string:text>', methods=['POST'])
def seh_start(text):
    # TODO: Use a queue or event to notify corresponding thread's driver
    time.sleep(0.5)
    return make_response(f'RUNNING: /dev/seh/{text}: XX Sensor')
    # return make_response('ERROR: XXX'), 500


@server.route('/stop/<string:text>', methods=['POST'])
def seh_stop(text):
    # TODO: Use a queue or event to notify corresponding thread's driver
    time.sleep(0.5)
    return make_response(f'STOPPED: /dev/seh/{text}: XX Sensor')
    # return make_response('ERROR: XXX'), 500


@server.route('/restart/<string:text>', methods=['POST'])
def seh_restart(text):
    # TODO: Use a queue or event to notify corresponding thread's driver
    time.sleep(0.5)
    return make_response(f'RESTARTED: /dev/seh/{text}: XX Sensor')
    # return make_response('ERROR: XXX'), 500


def start_web_server():
    Thread(target=lambda: server.run(host='0.0.0.0', port=WEB_SERVER_PORT, debug=True, use_reloader=False)).start()


if __name__ == '__main__':
    start_web_server()
