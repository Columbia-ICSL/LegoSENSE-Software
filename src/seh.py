import argparse

if __name__ == '__main__':
    # Parse Arguments

    parser = argparse.ArgumentParser(description='SensorHub Controller - Modify and Control SensorHub')
    subparsers = parser.add_subparsers(dest='command', help='Run seh {command} -h for additional help', required=True)

    # seh install <name> slotX
    parser_install = subparsers.add_parser(
        'install', help='Install a new SensorHub module into a specific slot')

    parser_install.add_argument('ModuleName', help='ModuleName')
    parser_install.add_argument('InstallTo',
                                help='slot1/slot2/slot3/slot4', choices=['slot1', 'slot2', 'slot3', 'slot4'])

    # seh uninstall <name> slotX
    parser_uninstall = subparsers.add_parser(
        'uninstall', help='Uninstall a new SensorHub module from a specific slot')
    parser_uninstall.add_argument('UninstallFrom',
                                  help='slot1/slot2/slot3/slot4', choices=['slot1', 'slot2', 'slot3', 'slot4'])

    # seh slotX start/stop/restart
    parser_slot1_ctl = subparsers.add_parser('slot1', help='start/stop/restart module on slot1')
    parser_slot2_ctl = subparsers.add_parser('slot2', help='start/stop/restart module on slot2')
    parser_slot3_ctl = subparsers.add_parser('slot3', help='start/stop/restart module on slot3')
    parser_slot4_ctl = subparsers.add_parser('slot4', help='start/stop/restart module on slot4')
    for p in [parser_slot1_ctl, parser_slot2_ctl, parser_slot3_ctl, parser_slot4_ctl]:
        p.add_argument('Operation', help='start/stop/restart',
                       choices=['start', 'stop', 'restart'])

    args = parser.parse_args()
    print(args)
