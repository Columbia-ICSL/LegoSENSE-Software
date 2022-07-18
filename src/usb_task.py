import os
import time
import serial
import datetime
import traceback
from log_util import get_logger
from serial.tools import list_ports

LOG_FOLDER = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'log')
logger = get_logger('IMU', file=os.path.join(LOG_FOLDER, datetime.datetime.now().strftime(f"imu_%y%m%d_%H%M%S.log")))

def get_port():
    ports = list_ports.comports()
    for port in ports:
        if port.description == 'USB Serial':
            return port.device
    raise RuntimeError('Cannot find USB device!')

save_interval = 50
last_save = time.time()
data_buf = ''
log_fname = os.path.join(LOG_FOLDER, datetime.datetime.now().strftime(f"%y%m%d_%H%M%S_imu.csv"))
i = 0

while True:
    try:
        with serial.Serial(get_port(), 115200) as ser:
            while True:
                try:
                    data = ser.readline()
                    data_buf += f'{time.time()},' + data.decode()
                    i += 1
                    if i % save_interval == 0:
                        logger.info(time.time() - last_save)
                        last_save = time.time()
                        with open(log_fname, 'a') as f:
                            f.write(data_buf)
                            data_buf = ''
                except KeyboardInterrupt:
                    raise # leave outside try except to handle
                except serial.serialutil.SerialException:
                    raise # leave outside to handle so it can restart serial
                except:
                    logger.error(traceback.format_exc())
                    time.sleep(1)
    except KeyboardInterrupt:
        break
    except:
        logger.error(traceback.format_exc())
        time.sleep(1)
