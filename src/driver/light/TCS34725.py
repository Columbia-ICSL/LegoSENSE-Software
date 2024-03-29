# Modified from https://github.com/ControlEverythingCommunity/TCS34725
import time
import smbus2

class TCS34725:
    def __init__(self, bus):
        self.bus = smbus2.SMBus(bus)
        # TCS34725 address, 0x29(41)
        # Select Enable register, 0x80(128)
        #		0x03(03)	Power ON, RGBC enable, RGBC Interrupt Mask not asserted
        #					Wait disable, Sleep After Interrupt not asserted
        self.bus.write_byte_data(0x29, 0x80, 0x03)
        # TCS34725 address, 0x29(41)
        # Select RGBC Timing register, 0x81(129)
        #		0x00(00)	ATIME : 700ms
        self.bus.write_byte_data(0x29, 0x81, 0x00)
        # TCS34725 address, 0x29(41)
        # Select Wait Time register, 0x83(131)
        #		0xFF(255)	WTIME : 2.4ms
        self.bus.write_byte_data(0x29, 0x83, 0xFF)
        # TCS34725 address 0x29(41)
        # Select Control register, 0x8F(143)
        #		0x00(00)	AGAIN is 1x
        self.bus.write_byte_data(0x29, 0x8F, 0x00)

    def read(self):
        # TCS34725 address 0x29(41)
        # Read data back from 0x94(148), 8 bytes
        # cData LSB, cData MSB, Red LSB, Red MSB, Green LSB, Green MSB
        # Blue LSB, Blue MSB 
        data = self.bus.read_i2c_block_data(0x29, 0x94, 8)
        
        # Convert the data
        cData = data[1] * 256 + data[0]
        red = data[3] * 256 + data[2]
        green = data[5] * 256 + data[4]
        blue = data[7] * 256 + data[6]
        
        # Calculate luminance
        luminance = (-0.32466 * red) + (1.57837 * green) + (-0.73191 * blue)
        return red, green, blue, cData, luminance
