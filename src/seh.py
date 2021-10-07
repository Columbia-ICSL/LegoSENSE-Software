#!/usr/bin/env python3
# SensorHub Command-line Control
import argparse
import requests

from config import WEB_SERVER_PORT, install_config, uninstall_config, list_config, edit_module_config


def send_to_sehd(command, module):
    assert command in ['start', 'stop', 'restart']
    url = f'http://127.0.0.1:{WEB_SERVER_PORT}/{command}/{module}'
    response = requests.post(url=url, timeout=10)
    if response.status_code > 200:
        # Error
        message = f'Error {response.status_code} {response.reason}:\n' + response.text
        raise RuntimeError(message)
    else:
        print(response.text)


def reload_service():
    url = f'http://127.0.0.1:{WEB_SERVER_PORT}/reload'
    response = requests.post(url=url, timeout=10)
    if response.status_code > 200:
        # Error
        message = f'Error {response.status_code} {response.reason}:\n' + response.text
        raise RuntimeError(message)
    else:
        print(response.text)


def install_driver(module_name, install_to):
    # TODO: Implement installation
    if install_config(module_name, install_to):
        print(f'Installed {module_name} to {install_to}')
        input('Press enter to restart SensorHub Service')
        reload_service()


def uninstall_driver(uninstall_from):
    # TODO: Implement uninstallation
    if uninstall_config(uninstall_from):
        print(f'Uninstalled {uninstall_from}')
        input('Press enter to restart SensorHub Service')
        reload_service()


def list_drivers():
    list_config()


if __name__ == '__main__':
    # Parse Arguments
    available_slots = list(range(1, 5))
    slots_description = [f'slot{x}' for x in available_slots]

    parser = argparse.ArgumentParser(description='SensorHub Controller - Modify and Control SensorHub')
    subparsers = parser.add_subparsers(dest='command', help='Run seh {command} -h for additional help', required=True)

    # > seh install <name> slotX
    parser_install = subparsers.add_parser(
        'install', help='Install a new SensorHub module into a specific slot')

    parser_install.add_argument('ModuleName', help='ModuleName')
    parser_install.add_argument('InstallTo', help='/'.join(slots_description), choices=slots_description)

    # > seh uninstall <name> slotX
    parser_uninstall = subparsers.add_parser(
        'uninstall', help='Uninstall a new SensorHub module from a specific slot')
    parser_uninstall.add_argument('UninstallFrom', help='/'.join(slots_description), choices=slots_description)

    # > seh list
    parser_list = subparsers.add_parser(
        'list', help='List installed SensorHub modules for each slots')

    # > seh slotX start/stop/restart
    for slot_x in available_slots:
        parser_slot = subparsers.add_parser(f'slot{slot_x}', help=f'start/stop/restart module on slot{slot_x}')
        parser_slot.add_argument('Operation', help='start/stop/restart',
                                 choices=['start', 'stop', 'restart'])

    # > seh edit slotX/module_name
    parser_edit = subparsers.add_parser(f'edit', help=f'Edit module configuration')
    parser_edit.add_argument('Name', help='slotX/module_name')

    # > seh reload
    parser_reload = subparsers.add_parser('reload', help='Reload SensorHub Service')

    args = parser.parse_args()

    if args.command == 'install':
        install_driver(args.ModuleName, args.InstallTo)
    elif args.command == 'uninstall':
        uninstall_driver(args.UninstallFrom)
    elif args.command == 'list':
        list_drivers()
    elif args.command.startswith('slot'):
        send_to_sehd(args.Operation, args.command)  # start/stop/restart, slotX
    elif args.command == 'edit':
        edit_module_config(args.Name)
    elif args.command == 'reload':
        reload_service()
    else:
        raise NotImplementedError(args)
