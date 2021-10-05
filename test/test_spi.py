import RPi.GPIO as GPIO
import time
import spidev

# SPI Bus 0/1
bus = 0
# CS Pin 0/1
device = 0

# Reset Module 1
GPIO.setmode(GPIO.BCM)
GPIO.setup(24, GPIO.OUT)
GPIO.output(24, 0)
time.sleep(1)
GPIO.output(24, 1)
time.sleep(1)

# Enable SPI
spi = spidev.SpiDev()
spi.open(bus, device)
spi.max_speed_hz = 500000
spi.mode = 0

# Read register
time.sleep(0.5)
for addr in range(0x00, 0x30):
    tx = [addr | (0 << 7), 0x00]
    rx = spi.xfer2(tx)
    print('%s: %s' % (hex(addr), hex(rx[1])))
