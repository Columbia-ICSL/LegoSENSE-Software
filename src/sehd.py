# SensorHub Background Process
import os
import errno
import tempfile
import argparse
import importlib

import fuse

import config
from worker import ModuleWorker, start_web_server


class SensorHubModuleManager:
    def __init__(self):
        self.installed_modules = config.INSTALLED_MODULES
        self.modules_worker = dict()
        self.start_workers()
        start_web_server()

    def __del__(self):
        self.stop_workers()

    def reload(self):
        self.stop_workers()

        # Reload config
        importlib.reload(config)
        self.installed_modules = config.INSTALLED_MODULES

        self.start_workers()

    def start_workers(self):
        for module, sensors in self.installed_modules.items():
            # TODO: Pass in some queue / event for webserver <--> sensor worker thread communication
            self.modules_worker[module] = ModuleWorker(module, sensors)

    def stop_workers(self):
        print('Stopping sensor workers....')
        for worker in self.modules_worker.values():
            worker.active = False
        for worker in self.modules_worker.values():
            worker.join()
        print('Sensor workers stopped')

    def get_modules(self):
        return list(self.installed_modules.keys())

    def get_sensors(self, module):
        return self.installed_modules[module]

    def get_module_worker(self, module):
        return self.modules_worker[module]

    def get_sensor_filesize(self, module, sensor):
        return len(self.modules_worker[module].sensor[sensor])

    def get_sensor_data(self, module, sensor, offset, length):
        return self.modules_worker[module].sensor[sensor][offset: offset + length]


class SensorHubFSInterface(fuse.Operations):
    def __init__(self, module_manager):
        # Get default stats for an empty directory and empty file.
        # The temporary directory and file are automatically deleted.
        with tempfile.TemporaryDirectory() as tmp_dir:
            self.stat_dir_template = \
                self._stat2dict(os.lstat(tmp_dir))

        with tempfile.NamedTemporaryFile() as tmp_file:
            self.stat_file_template = \
                self._stat2dict(os.lstat(tmp_file.name))

        self.model = module_manager

    # Given a 'stat_result' object, convert it into a Python dictionary.
    @staticmethod
    def _stat2dict(stat_result):
        stat_keys = ('st_atime', 'st_ctime', 'st_gid', 'st_mode',
                     'st_mtime', 'st_nlink', 'st_size', 'st_uid')

        return dict((key, getattr(stat_result, key)) for key in stat_keys)

    def _parse_path(self, path):
        # valid path: /<module>/<sensor>
        parsed = path.split(os.sep)
        module, sensor = None, None
        if len(parsed) == 2 and parsed[-1] in self.model.get_modules():
            module = parsed[-1]
        elif len(parsed) == 3 and parsed[-2] in self.model.get_modules():
            if parsed[-1] in self.model.get_sensors(parsed[-2]):
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
                stat['st_size'] = self.model.get_sensor_filesize(module, sensor)
                return stat
        else:
            # For all other files/directories, return the stats from the OS.
            return self._stat2dict(os.lstat(path))

    # Implementation for `ls`
    def readdir(self, path, fh):
        module, sensor = self._parse_path(path)
        if module is None:
            # Top level directories: module X
            return ['.', '..'] + self.model.get_modules()
        elif module is not None and sensor is None:
            # Module directory
            return ['.', '..'] + self.model.get_sensors(module)
        else:
            print('Error readdir: ' + repr({'path': path}))
            raise fuse.FuseOSError(errno.EIO)

    # Implementation for read
    def read(self, path, length, offset, fh):
        module, sensor = self._parse_path(path)
        if module is None:
            print('Error read: ' + repr({'path': path, 'buf': length, 'offset': offset}))
            raise fuse.FuseOSError(errno.EIO)
        return self.model.get_sensor_data(module, sensor, offset, length)

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


def start_fuse(mount_point):
    # FIXME: HACK: manager has to be in this function for its __del__ to work properly at program termination
    manager = SensorHubModuleManager()
    fs_interface = SensorHubFSInterface(manager)
    fuse.FUSE(fs_interface, mount_point, nothreads=False, foreground=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("mount_point", help="Mount point for the Virtual File System")
    args = parser.parse_args()

    start_fuse(args.mount_point)
