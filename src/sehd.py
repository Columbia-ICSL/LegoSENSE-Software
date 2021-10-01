# SensorHub Background Process
import os
import time
import errno
import tempfile
import argparse
import datetime
from threading import Thread

import fuse

# TODO: this should be loaded from config
MODULES = {
    'M1': [],
    'M2': [],
    'M3': [],
    'M4': ['co2', 'tempHum', 'airQua']
}


# TODO: Handle RuntimeError(1): mount point is itself a fuse volume -- umount -f /absolute/path/to/mount_point

class SensorHubModule(Thread):
    def __init__(self, module, sensors):
        assert isinstance(module, str)
        assert isinstance(sensors, list)

        assert len(sensors) == len(MODULES[module])
        self.module = module
        self.sensor = {}
        for i in sensors:
            self.sensor[i] = f"Module {self.module}: {i}\n".encode()
        print(f"{self.module} init")

        Thread.__init__(self)
        self.start()

    def run(self):
        # TODO: Gracefully kill the thread
        while True:
            print(f'{self.module} working...')
            timestr = (datetime.datetime.now() + datetime.timedelta(hours=3)).strftime("[%H:%M:%S.%f]")

            for i in self.sensor.keys():
                hum = 10
                temp = 20
                self.sensor[i] += f'{timestr}\t{temp:.2f}\t{hum:.2f}\n'.encode()
            time.sleep(0.2)


class SensorHubDaemon(fuse.Operations):
    def __init__(self):
        # Get default stats for an empty directory and empty file.
        # The temporary directory and file are automatically deleted.
        with tempfile.TemporaryDirectory() as tmp_dir:
            self.stat_dir_template = \
                self._stat2dict(os.lstat(tmp_dir))

        with tempfile.NamedTemporaryFile() as tmp_file:
            self.stat_file_template = \
                self._stat2dict(os.lstat(tmp_file.name))

        # Initialize modules
        self.modules = dict()
        for module, sensors in MODULES.items():
            self.modules[module] = SensorHubModule(module, sensors)

    # Given a 'stat_result' object, convert it into a Python dictionary.
    @staticmethod
    def _stat2dict(stat_result):
        stat_keys = ('st_atime', 'st_ctime', 'st_gid', 'st_mode',
                     'st_mtime', 'st_nlink', 'st_size', 'st_uid')

        return dict((key, getattr(stat_result, key)) for key in stat_keys)

    @staticmethod
    def _parse_path(path):
        # valid path: /<module>/<sensor>
        parsed = path.split(os.sep)
        module, sensor = None, None
        if len(parsed) == 2 and parsed[-1] in MODULES.keys():
            module = parsed[-1]
        elif len(parsed) == 3 and parsed[-2] in MODULES.keys():
            if parsed[-1] in MODULES[parsed[-2]]:
                module, sensor = parsed[-2:]
        return module, sensor

    # ------------------- Filesystem Handlers -------------------
    def getattr(self, path, fh=None):
        module, sensor = self._parse_path(path)
        if module is not None:
            if sensor is None:
                return self.stat_dir_template
            else:
                # Use default stats, with size modified
                stat = dict(self.stat_file_template)  # Create a copy before modifying
                stat['st_size'] = len(self.modules[module].sensor[sensor])
                return stat
        else:
            # For all other files/directories, return the stats from the OS.
            return self._stat2dict(os.lstat(path))

    # Implementation for `ls`
    def readdir(self, path, fh):
        module, sensor = self._parse_path(path)
        if module is None:
            # Top level directories: module X
            return ['.', '..'] + list(MODULES.keys())
        elif module is not None and sensor is None:
            # Module directory
            return ['.', '..'] + MODULES[module]
        else:
            print('Error readdir: ' + repr({'path': path}))
            raise fuse.FuseOSError(errno.EIO)

    # Implementation for read
    def read(self, path, length, offset, fh):
        module, sensor = self._parse_path(path)
        if module is None:
            print('Error read: ' + repr({'path': path, 'buf': length, 'offset': offset}))
            raise fuse.FuseOSError(errno.EIO)
        inst = self.modules[module]
        return inst.sensor[sensor][offset: offset + length]

    # Implementation for write
    def write(self, path, buf, offset, fh):
        print(f'write{path}')
        module, sensor = self._parse_path(path)
        if module is None:
            print('Error write: ' + repr({'path': path, 'buf': buf, 'offset': offset}))
            raise fuse.FuseOSError(errno.EIO)
        print('Write not implemented')
        print({'path': path, 'buf': buf, 'offset': offset})

    # Implementation for close
    def release(self, path, fh):
        print(f'release{path}')
        module, sensor = self._parse_path(path)
        if module is None:
            print('Error release: ' + repr({'path': path}))
            raise fuse.FuseOSError(errno.EIO)
        print('Release not implemented')
        print({'path': path})


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("mount_point", help="Mount point for the Virtual File System")
    args = parser.parse_args()

    fuse.FUSE(SensorHubDaemon(),
              args.mount_point,
              nothreads=False,
              foreground=True)
