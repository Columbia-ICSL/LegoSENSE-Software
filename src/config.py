# Configuration Utility for SensorHub Service
import os
import json

WEB_SERVER_PORT = 1515


def save_config(config):
    with open('config.json', 'w') as f:
        json.dump(config, f)


if not os.path.exists('config.json'):
    default_module_cfg = dict(zip(['slot1', 'slot2', 'slot3', 'slot4'], ['' for i in range(4)]))
    save_config(default_module_cfg)

with open('config.json', 'r') as f:
    INSTALLED_MODULES = json.load(f)


def install_config(module_name, install_to):
    # NOTE: Caller responsible for reloading the system
    if INSTALLED_MODULES[install_to] == '':
        INSTALLED_MODULES[install_to] = module_name
        save_config(INSTALLED_MODULES)
        return True
    else:
        conflict = INSTALLED_MODULES[install_to]
        print(f'ERROR: {install_to} has {conflict} installed. '
              f'Please uninstall it first with seh uninstall {install_to}. '
              f'No change was made.')
        return False


def uninstall_config(uninstall_from):
    # NOTE: Caller responsible for reloading the system
    if INSTALLED_MODULES[uninstall_from] != '':
        INSTALLED_MODULES[uninstall_from] = ''
        save_config(INSTALLED_MODULES)
        return True
    else:
        print(f'ERROR: {uninstall_from} has no module installed. No change was made.')
        return False


def list_config():
    for slot in sorted(INSTALLED_MODULES.keys()):
        if INSTALLED_MODULES[slot] == '':
            print(f'{slot}:\tEmpty')
        else:
            module_name = INSTALLED_MODULES[slot]
            print(f'{slot}:\t{module_name}')
