import os
import subprocess
from flask import Flask, request, make_response, jsonify

src_dir = os.path.dirname((os.path.dirname(os.path.realpath(__file__))))
log_dir = os.path.join(src_dir, 'log')
app = Flask(__name__)

def os_command(command_list, notify=True):
    """ Sends OS command and returns output """
    assert isinstance(command_list, list)
    try:
        result = subprocess.check_output(command_list)
        if isinstance(result, bytes):
            result = result.decode('utf-8')
            if notify:
                print("[CMD]", " ".join(command_list), '\n', result)
    except subprocess.CalledProcessError as exc:
        print("[CMD]", " ".join(command_list))
        result = exc.output
        print("[CMD]", " ".join(command_list))
        print("[ERR]", result)

    return result

@app.route('/', methods=['GET'])
def ping():
    result = os_command(['date'])
    ret = f'SensorHub Controller is live. System time: {result}'
    return make_response(ret)


@app.route('/ls_log', methods=['GET'])
def ls_log():
    files = {}
    if os.path.exists(log_dir):
        log_files = os.listdir(log_dir)
        log_files = [i for i in log_files if i.endswith('.csv')]
        for log_file in log_files:
            size = os.path.getsize(os.path.join(log_dir, log_file))
            files[log_file] = size
    return jsonify(files)


@app.route('/get_time', methods=['GET'])
def get_os_time():
    result = os_command(['date'])
    return make_response(result)


@app.route('/set_time', methods=['POST'])
def set_os_time():
    configs = request.headers
    if 'Time' in configs.keys():
        result = os_command(['date', '-s', configs['time']])
    else:
        return make_response('Missing Time in headers'), 400
    return make_response(result)


@app.route('/shutdown', methods=['POST'])
def shutdown_system():
    result = os_command(['/sbin/shutdown', '-h', 'now'])
    return make_response(result)


@app.route('/reboot', methods=['POST'])
def reboot_system():
    result = os_command(['/sbin/reboot', 'now'])
    return make_response(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1516)
