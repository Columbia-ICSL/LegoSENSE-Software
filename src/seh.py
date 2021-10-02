#!/usr/bin/env python3
import argparse

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

    # > seh slotX start/stop/restart
    for slot_x in available_slots:
        parser_slot = subparsers.add_parser(f'slot{slot_x}', help=f'start/stop/restart module on slot{slot_x}')
        parser_slot.add_argument('Operation', help='start/stop/restart',
                                 choices=['start', 'stop', 'restart'])

    args = parser.parse_args()

    if args.command == 'install':
        raise NotImplementedError(f'Install {args.ModuleName} to {args.InstallTo}')
    elif args.command == 'uninstall':
        raise NotImplementedError(f'Uninstall {args.ModuleName} from {args.InstallTo}')
    elif args.command.startswith('slot'):
        slot = args.command.lstrip('slot')
        raise NotImplementedError(f'{args.Operation} {slot}')
    else:
        raise NotImplementedError(args)
