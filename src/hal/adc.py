import RPi.GPIO as GPIO
import time
import spidev

# SPI Bus 0/1
bus = 1
# CS Pin 0/1
device = 2

# Enable SPI
spi = spidev.SpiDev()
spi.open(bus, device)
spi.max_speed_hz = 500000
spi.mode = 0

# Read register
time.sleep(0.5)

channels = {
    0: 0x00,
    1: 0x08,
    2: 0x10,
    3: 0x18,
    4: 0x20,
    5: 0x28,
    6: 0x30,
    7: 0x38
}

for channel, tx in channels.items():
    rx = spi.xfer([tx, 0x00])
    result = (rx[1] / 4096) * 3.3
    print('CH%d: %.3fV\t(%d)' % (channel, result, rx[1]))
