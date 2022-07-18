import os
import pickle
import subprocess
from flask import Flask, request, make_response, jsonify

src_dir = os.path.dirname((os.path.dirname(os.path.realpath(__file__))))
log_dir = os.path.join(src_dir, 'log')
event_file = os.path.join(log_dir, 'events.log')
event_state_file = os.path.join(log_dir, 'event_state.pkl')

app = Flask(__name__)


def os_command(command_list, notify=True, cwd=None):
    """ Sends OS command and returns output """
    assert isinstance(command_list, list)
    try:
        if cwd is None:
            result = subprocess.check_output(command_list)
        else:
            result = subprocess.check_output(command_list, cwd=cwd)
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


def ensure_event_file_initialized():
    if not os.path.exists(event_file):
        with open(event_file, 'w') as f:
            f.write('event_type,event_start,event_end\n')

    if not os.path.exists(event_state_file):
        with open(event_state_file, 'wb') as f:
            event_state = {
                'current': None,
                'start': -1,
                'id': -1
            }
            pickle.dump(event_state, f)


def load_event_state():
    ensure_event_file_initialized()
    with open(event_state_file, 'rb') as f:
        return pickle.load(f)


def save_event_state(state):
    assert isinstance(state, dict)
    assert all(i in state.keys() for i in ['current', 'start', 'id'])

    with open(event_state_file, 'wb') as f:
        pickle.dump(state, f)


@app.route('/get_events', methods=['GET'])
def get_events():
    ensure_event_file_initialized()

    events = {}
    with open(event_file, 'r') as f:
        events_log = f.readlines()[1:]
        for event in events_log:
            event_id, event_name, event_start, event_end = event.strip().split(',')
            events[event_id] = {'name': event_name, 'start': event_start, 'end': event_end}
    return jsonify({'state': load_event_state(), 'events': events})


@app.route('/add_event', methods=['POST'])
def add_event():
    configs = request.headers
    print(list(configs.keys()))
    if any(i not in configs.keys() for i in ['Event-Type', 'Event-Start', 'Event-End', 'Callback-Url']):
        return make_response('Missing Event-Type, Event-Start, Event-End, and/or Callback-URL in headers'), 400

    event_start = int(configs['Event-Start'])
    event_end = int(configs['Event-End'])
    event_type = configs['Event-Type']
    callback_url = configs['Callback-Url']

    ensure_event_file_initialized()
    event_state = load_event_state()
    if event_state['current'] is None:
        # Start of an event
        if event_start == -1:
            return make_response('Server has no current event but received empty start time'), 400
        if event_end != -1:
            return make_response('Server has no current event but received non empty end time'), 400
        event_state['current'] = event_type
        event_state['start'] = event_start
        event_state['id'] = event_state['id'] + 1
        save_event_state(event_state)
    else:
        # End of an event
        if event_start != -1:
            return make_response(
                f'Server has current event {event_state["current"]} but received non empty start time'), 400
        if event_end == -1:
            return make_response(f'Server has current event {event_state["current"]} but received empty end time'), 400
        if event_type != event_state['current']:
            return make_response(f'Server has current event {event_state["current"]} but received a different ending event {event_type}'), 400
        with open(event_file, 'a') as f:
            f.write(f'{event_state["id"]},{event_state["current"]},{event_state["start"]},{event_end}\n')

        event_state['current'] = None
        event_state['start'] = -1
        save_event_state(event_state)

    return make_response('OK'), 200


@app.route('/get_version', methods=['GET'])
def get_sw_version():
    result = os_command(['git', 'log', '-1', '--format=%h'], cwd=os.path.dirname(src_dir))
    result += '\t' + os_command(['git', 'log', '-1', '--format=%cd'], cwd=os.path.dirname(src_dir))
    return make_response(result)


@app.route('/upgrade', methods=['GET', 'POST'])
def upgrade_sw():
    result = os_command(['git', 'pull'], cwd=os.path.dirname(src_dir))
    return make_response(result)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1516)
