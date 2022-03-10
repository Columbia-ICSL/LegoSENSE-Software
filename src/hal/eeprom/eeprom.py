#!/usr/bin/env python3
# Modified from https://github.com/ARizzo35/python-eeprom
import os
import time
import subprocess


def check_device_exists(bus, addr):
    if not hasattr(check_device_exists, 'i2cdetect_bin'):
        check_device_exists.i2cdetect_bin = subprocess.getoutput('which i2cdetect')
    if check_device_exists.i2cdetect_bin:
        cp = subprocess.run(
            [check_device_exists.i2cdetect_bin, '-y', str(bus), str(addr), str(addr)],
            capture_output=True
        )
        if cp.returncode != 0:
            if "Permission denied" in cp.stderr.decode():
                raise PermissionError(cp.stderr.decode())
            return False
        if '--' in cp.stdout.decode():
            return False
    return True

EEPROM_TYPES = {
    "24c00": int(128 / 8),
    "24c01": int(1024 / 8),
    "24c02": int(2048 / 8),
    "24c04": int(4096 / 8),
    "24c08": int(8192 / 8),
    "24c16": int(16384 / 8),
    "24c32": int(32768 / 8),
    "24c64": int(65536 / 8),
    "24c128": int(131072 / 8),
    "24c256": int(262144 / 8),
    "24c512": int(524288 / 8),
    "24c1024": int(1048576 / 8),
    "24c2048": int(2097152 / 8),
}

SYSFS_I2C_DEVICES_DIR = os.environ.get("SYSFS_I2C_DEVICES_DIR", "/sys/bus/i2c/devices")


class EEPROMError(IOError):
    pass

class EEPROM():

    _eeprom_fd = None
    _busdir = None
    _devdir = None

    @property
    def name(self):
        if getattr(self, '_name', None) is None:
            self._name = f"{self._bus}-{self._addr:04x}"
        return self._name

    def __init__(self, dev_type, i2c_bus, i2c_addr):
        # Check device type
        if not isinstance(dev_type, str) or dev_type not in EEPROM_TYPES.keys():
            raise ValueError(f"Invalid dev_type: {dev_type}")
        self._type = dev_type
        self._size = EEPROM_TYPES[dev_type]
        # Check I2C bus
        self._busdir = os.path.join(SYSFS_I2C_DEVICES_DIR, f"i2c-{i2c_bus}")
        if not isinstance(i2c_bus, int) or not os.path.isdir(self._busdir):
            raise ValueError(f"Invalid i2c_bus: {i2c_bus}")
        self._bus = i2c_bus
        # Check I2C address
        if not isinstance(i2c_addr, int):
            raise ValueError(f"Invalid i2c_addr: {i2c_addr}")
        if not check_device_exists(i2c_bus, i2c_addr):
            raise ValueError(f"I2C device not exist on: {hex(i2c_addr)}")
        self._addr = i2c_addr
        # Open device
        self.open()

    def __del__(self):
        self.close()

    def __enter__(self):
        return self

    def __exit__(self, t, value, traceback):
        self.close()

    def _create_device(self):
        try:
            with open(os.path.join(self._busdir, "new_device"), 'w') as f:
                f.write(f"{self._type} {self._addr}\n")
        except IOError as e:
            print(os.path.join(self._busdir, "new_device"))
            raise EEPROMError(e.errno, f"Creating Device: {e.strerror}")

    def _delete_device(self):
        if self._devdir and os.path.isdir(self._devdir):
            try:
                fd = os.open(os.path.join(self._busdir, "delete_device"), os.O_WRONLY)
                os.write(fd, f"{self._addr}\n".encode())
                os.close(fd)
            except OSError as e:
                raise EEPROMError(e.errno, f"Deleting Device: {e.strerror}")

    def open(self):
        if self._devdir is None:
            self._devdir = os.path.join(SYSFS_I2C_DEVICES_DIR, self.name)
        if not os.path.isdir(self._devdir):
            self._create_device()
        for i in range(5):
            if not os.path.isfile(os.path.join(self._devdir, 'eeprom')):
                print("eeprom file not found.. retrying in 200ms")
                time.sleep(0.2)
            break
        if not os.path.isfile(os.path.join(self._devdir, 'eeprom')):
            raise EEPROMError("Error creating device, eeprom file not found")
        try:
            self._eeprom_fd = os.open(os.path.join(self._devdir, 'eeprom'), os.O_RDWR)
        except OSError as e:
            raise EEPROMError(e.errno, f"Opening EEPROM: {e.strerror}")

    def close(self):
        if self._eeprom_fd:
            os.close(self._eeprom_fd)
        # Leave device open for multiple access?
        self._delete_device()

    def read(self, size, addr=0):
        if (size + addr) > self._size:
            raise EEPROMError(f"Cannot read {size} bytes @ address 0x{addr:x} (EEPROM Size: {self._size})")
        try:
            os.lseek(self._eeprom_fd, addr, os.SEEK_SET)
            data = b''
            while len(data) < size:
                data += os.read(self._eeprom_fd, size - len(data))
        except OSError as e:
            raise EEPROMError(e.errno, f"EEPROM Read: {e.strerror}")
        return data

    def write(self, data, addr=0):
        size = len(data)
        if (size + addr) > self._size:
            raise EEPROMError(f"Cannot write {size} bytes @ address 0x{addr:08x} (EEPROM Size: {self._size})")
        try:
            os.lseek(self._eeprom_fd, addr, os.SEEK_SET)
            written = 0
            while written < size:
                written += os.write(self._eeprom_fd, data[written:])
        except OSError as e:
            raise EEPROMError(e.errno, f"EERPOM Write: {e.strerror}")
        return written

