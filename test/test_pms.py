#!/usr/bin/env python
import time
import RPi.GPIO as GPIO
from pms5003 import PMS5003

print("""all.py - Continously print all data values.
Press Ctrl+C to exit!
""")

# Reset Module 1
GPIO.setmode(GPIO.BCM)
GPIO.setup(24, GPIO.OUT)
GPIO.output(24, 0)
time.sleep(0.1)
GPIO.output(24, 1)
time.sleep(0.1)

# Configure the PMS5003 for Enviro+
pms5003 = PMS5003(
    device='/dev/ttyS0',
    baudrate=9600,
    pin_enable=22,
    pin_reset=27
)

try:
    while True:
        data = pms5003.read()
        print(data)

except KeyboardInterrupt:
    pass