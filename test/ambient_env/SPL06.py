#!/usr/bin/env python
# https://github.com/rv701/SPL06-007_RASPI_Python/blob/master/spl06-test.py

import time
import smbus2 as smbus
import numpy as np

# SPL06-007 I2C address
SPL06_I2C_ADDR = 0x77

class SPL06:
    def __init__(self, bus=1):
        self.bus = smbus.SMBus(bus)
        # Set pressure configuration register (PRS_CFG)
        # 8 measurements per sec, 8X oversampling
        self.bus.write_byte_data(SPL06_I2C_ADDR, 0x06, int("00110011", 2))
        # Set temperature configuration register (TMP_CFG)
        # 8 measurements per sec, 8X oversampling
        self.bus.write_byte_data(SPL06_I2C_ADDR, 0x07, int("10110011", 2))
        # Set measurement register
        self.bus.write_byte_data(SPL06_I2C_ADDR, 0x08, 0x07) # Continuous temp & pressure measurement
        # Set configuration register
        self.bus.write_byte_data(SPL06_I2C_ADDR, 0x09, 0x00) # FIFO

        self._get_calibration()

    def get_pressure(self):
        """ Return measured pressure in mb """
        traw = self._get_traw()
        t_scale = self._get_temperature_scale_factor()
        traw_sc = traw / t_scale
        # temp_c = ((c0) * 0.5) + ((c1) * traw_sc)
        # temp_f = (temp_c * 9/5) + 32
        praw = self._get_praw()
        p_scale = self._get_pressure_scale_factor()
        praw_sc = praw / p_scale
        pcomp = self.c00+praw_sc*(self.c10+praw_sc*(self.c20+praw_sc*self.c30))+traw_sc*self.c01+traw_sc*praw_sc*(self.c11+praw_sc*self.c21)
        
        return round(pcomp / 100, 4)
        # print("Measured Air Pressure: ", "{:.2f}".format(pcomp/100), " mb")

        # local_sealevel = 1011.3
        # print("Local Airport Sea Level Pressure: ", local_sealevel)

        # altitude = self._get_altitude(pcomp, local_sealevel)
        # print("altitude:",  "{:.1f}".format(altitude), " m")

        # altitude_f = altitude * 3.281
        # print("altitude",  "{:.1f}".format(altitude_f), " ft")

    def _get_calibration(self):
        self.c0 = self._get_c0()
        self.c1 = self._get_c1()
        self.c00 = self._get_c00()
        self.c10 = self._get_c10()
        self.c01 = self._get_c01()
        self.c11 = self._get_c11()
        self.c20 = self._get_c20()
        self.c21 = self._get_c21()
        self.c30 = self._get_c30()

    def print_calibration(self):
        print("c0:", self.c0)
        print("c1:", self.c1)
        print("c00:", self.c00)
        print("c10:", self.c10)
        print("c01:", self.c01)
        print("c11:", self.c11)
        print("c20:", self.c20)
        print("c21:", self.c21)
        print("c30:", self.c30)


    def print_sensor_settings_reg(self):
        # Read SPL06-007 Device ID
        id = self.bus.read_byte_data(SPL06_I2C_ADDR, 0x0D)
        print("ID:", id)

        # Read pressure configuration register
        var = self.bus.read_byte_data(SPL06_I2C_ADDR, 0x06)
        print("PRG_CFG:", bin(var))

        var = self.bus.read_byte_data(SPL06_I2C_ADDR, 0x07)
        print("TMP_CFG:", bin(var))

        var = self.bus.read_byte_data(SPL06_I2C_ADDR, 0x08)
        print("MEAS_CFG:", bin(var))

        var = self.bus.read_byte_data(SPL06_I2C_ADDR, 0x09)
        print("CFG_REG:", bin(var))

        var = self.bus.read_byte_data(SPL06_I2C_ADDR, 0x0A)
        print("INT_STS:", bin(var))

        var = self.bus.read_byte_data(SPL06_I2C_ADDR, 0x0B)
        print("FIFO_STS:", bin(var))
    
    def _get_c0(self):
        tmp_MSB = self.bus.read_byte_data(SPL06_I2C_ADDR, 0x10)
        tmp_LSB = self.bus.read_byte_data(SPL06_I2C_ADDR, 0x11)

        tmp_LSB = tmp_LSB >> 4;
        tmp = tmp_MSB << 4 | tmp_LSB

        if (tmp & (1 << 11)):
            tmp = tmp | 0xF000

        return np.int16(tmp)

    def _get_c1(self):
        tmp_MSB = self.bus.read_byte_data(SPL06_I2C_ADDR, 0x11)
        tmp_LSB = self.bus.read_byte_data(SPL06_I2C_ADDR, 0x12)

        tmp_LSB = self.bus.read_byte_data(SPL06_I2C_ADDR, 0xF)
        tmp = tmp_MSB << 8 | tmp_LSB

        if (tmp & (1 << 11)):
            tmp = tmp | 0xF000

        return np.int16(tmp)

    def _get_c00(self):
        tmp_MSB = self.bus.read_byte_data(SPL06_I2C_ADDR, 0x13)
        tmp_LSB = self.bus.read_byte_data(SPL06_I2C_ADDR, 0x14)
        tmp_XLSB = self.bus.read_byte_data(SPL06_I2C_ADDR, 0x15)

        tmp = np.uint32(tmp_MSB << 12) | np.uint32(tmp_LSB << 4) | np.uint32(tmp_XLSB >> 4)

        if(tmp & (1 << 19)):
            tmp = tmp | 0XFFF00000
        
        return np.int32(tmp)

    def _get_c10(self):
        tmp_MSB = self.bus.read_byte_data(SPL06_I2C_ADDR, 0x15)
        tmp_LSB = self.bus.read_byte_data(SPL06_I2C_ADDR, 0x16)
        tmp_XLSB = self.bus.read_byte_data(SPL06_I2C_ADDR, 0x17)

        tmp_MSB = tmp_MSB & 0xF

        #tmp = tmp_MSB << 8 | tmp_LSB
        #tmp = tmp << 8
        tmp = np.uint32(tmp_MSB << 16) | np.uint32(tmp_LSB << 8) | np.uint32(tmp_XLSB)

        if(tmp & (1 << 19)):
            tmp = tmp | 0XFFF00000

        return np.int32(tmp)

    def _get_c01(self):
        tmp_MSB = self.bus.read_byte_data(SPL06_I2C_ADDR, 0x18)
        tmp_LSB = self.bus.read_byte_data(SPL06_I2C_ADDR, 0x19)

        tmp = (tmp_MSB << 8) | tmp_LSB

        return np.int16(tmp)

    def _get_c11(self):
        tmp_MSB = self.bus.read_byte_data(SPL06_I2C_ADDR, 0x1A)
        tmp_LSB = self.bus.read_byte_data(SPL06_I2C_ADDR, 0x1B)

        tmp = (tmp_MSB << 8) | tmp_LSB

        return np.int16(tmp)

    def _get_c20(self):
        tmp_MSB = self.bus.read_byte_data(SPL06_I2C_ADDR, 0x1C)
        tmp_LSB = self.bus.read_byte_data(SPL06_I2C_ADDR, 0x1D)

        tmp = (tmp_MSB << 8) | tmp_LSB

        return np.int16(tmp)

    def _get_c21(self):
        tmp_MSB = self.bus.read_byte_data(SPL06_I2C_ADDR, 0x1E)
        tmp_LSB = self.bus.read_byte_data(SPL06_I2C_ADDR, 0x1F)

        tmp = (tmp_MSB << 8) | tmp_LSB

        return np.int16(tmp)

    def _get_c30(self):
        tmp_MSB = self.bus.read_byte_data(SPL06_I2C_ADDR, 0x20)
        tmp_LSB = self.bus.read_byte_data(SPL06_I2C_ADDR, 0x21)

        tmp = (tmp_MSB << 8) | tmp_LSB

        return np.int16(tmp)

    def _get_traw(self):
        tmp_MSB = self.bus.read_byte_data(SPL06_I2C_ADDR, 0x03)
        tmp_LSB = self.bus.read_byte_data(SPL06_I2C_ADDR, 0x04)
        tmp_XLSB = self.bus.read_byte_data(SPL06_I2C_ADDR, 0x05)

        tmp = np.uint32(tmp_MSB << 16) | np.uint32(tmp_LSB << 8) | np.uint32(tmp_XLSB)

        if(tmp & (1 << 23)):
            tmp = tmp | 0XFF000000

        return np.int32(tmp)

    def _get_temperature_scale_factor(self):
        tmp_Byte = self.bus.read_byte_data(SPL06_I2C_ADDR, 0x07)

        tmp_Byte = tmp_Byte & 0B111

        if(tmp_Byte == 0B000):
            k = 524288.0

        if(tmp_Byte == 0B001):
            k = 1572864.0

        if(tmp_Byte == 0B010):
            k = 3670016.0

        if(tmp_Byte == 0B011):
            k = 7864320.0

        if(tmp_Byte == 0B100):
            k = 253952.0

        if(tmp_Byte == 0B101):
            k = 516096.0

        if(tmp_Byte == 0B110):
            k = 1040384.0

        if(tmp_Byte == 0B111):
            k = 2088960.0 

        return k

    def _get_praw(self):
        tmp_MSB = self.bus.read_byte_data(SPL06_I2C_ADDR, 0x00)
        tmp_LSB = self.bus.read_byte_data(SPL06_I2C_ADDR, 0x01)
        tmp_XLSB = self.bus.read_byte_data(SPL06_I2C_ADDR, 0x02)

        tmp = np.uint32(tmp_MSB << 16) | np.uint32(tmp_LSB << 8) | np.uint32(tmp_XLSB)

        if(tmp & (1 << 23)):
            tmp = tmp | 0XFF000000

        return np.int32(tmp)

    def _get_pressure_scale_factor(self):
        tmp_Byte = self.bus.read_byte_data(SPL06_I2C_ADDR, 0x06)

        tmp_Byte = tmp_Byte & 0B111

        if(tmp_Byte == 0B000):
            k = 524288.0

        if(tmp_Byte == 0B001):
            k = 1572864.0

        if(tmp_Byte == 0B010):
            k = 3670016.0

        if(tmp_Byte == 0B011):
            k = 7864320.0

        if(tmp_Byte == 0B100):
            k = 253952.0

        if(tmp_Byte == 0B101):
            k = 516096.0

        if(tmp_Byte == 0B110):
            k = 1040384.0

        if(tmp_Byte == 0B111):
            k = 2088960.0

        return k

    def _get_altitude(pressure, pressure_sealevel):
        pressure /= 100
        altitude = 44330 * (1.0 - pow((pressure / pressure_sealevel), 0.1903))
        return altitude

if __name__ == "__main__":
    spl = SPL06()
    while True:
        print(spl.get_pressure())
        time.sleep(0.1)