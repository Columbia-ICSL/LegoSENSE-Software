#!/usr/bin/env python
import time
import RPi.GPIO as GPIO
from pms5003 import PMS5003

from datetime import datetime
import pytz
est = pytz.timezone('US/Eastern')

print("""all.py - Continously print all data values.
Press Ctrl+C to exit!
""")

# Reset Module 1
# GPIO.setmode(GPIO.BCM)
# GPIO.setup(24, GPIO.OUT)
# GPIO.output(24, 0)
# time.sleep(0.1)
# GPIO.output(24, 1)
# time.sleep(0.1)

reset_pins = {
    1: 24,
    2: 25,
    3: 26,
    4: 27
}

device_addresses = {
    1: '/dev/ttyS0',
    2: '/dev/ttyAMA1',
    3: '/dev/ttyAMA2',
    4: '/dev/ttyAMA3'
}

module = 4

# Configure the PMS5003 for Enviro+
pms5003 = PMS5003(
    device=device_addresses[module],
    baudrate=9600,
    pin_enable=reset_pins[module],  # We did not connect enable
    pin_reset=reset_pins[module]
)

try:
    filename = datetime.now(est).strftime('PMS_%H_%M_%S.csv')
    # Header
    with open(filename, 'a') as f:
        f.write('Year,Month,Day,Hour,Minute,Second,PM1.0_ultrafine,PM2.5_combustion_particles__organic_compounds__metals,PM10__dust__pollen__mould_spores,PM1.0_atoms_env,PM2.5_atoms_env,PM10_atoms_env,LT0.3um,LT0.5um,LT1.0um,LT2.5um,LT5.0um,LT10um\n')
    
    while True:
        data = pms5003.read()
        # print(data)
        # print(data.data[:-2])
        with open(filename, 'a') as f:
            time = datetime.now(est).strftime('%Y,%m,%d,%H,%M,%S,')
            data = ','.join(map(str, data.data[:-2]))
            log = time + data + '\n'
            f.write(log)
            print(log)


except KeyboardInterrupt:
    pass