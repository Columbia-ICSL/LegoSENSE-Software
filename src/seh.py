import argparse

from hal import ResourceManager

RM = ResourceManager()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-install', dest='install', action='store', required=False,
                        help='Install a new module', type=str)
    args = parser.parse_args()
    print(args.install)
