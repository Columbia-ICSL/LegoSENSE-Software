
from mpu6050 import mpu6050
import time

'''
This test code uses the library foudn at https://github.com/m-rtijn/mpu6050

To install this:
    1. Git clone
    2. cd to the cloned dir
    3. edit mpu6050/mpu6050.py 
    4. change smbus to smbus2
    5. install using 'pip install .' from within the cloned repo

'''
sensor = mpu6050(0x68)

print("Accel Range: %d g" %sensor.read_accel_range())
print("gyro Range: %d degrees/sec" %sensor.read_gyro_range())

while True:
    acc_data = sensor.get_accel_data()
    gyr_data = sensor.get_gyro_data()
    print("ACC X: %3d Y: %3d Z: %3d\tGYRO X: %3d Y: %3d Z: %3d" %\
            (acc_data['x'], acc_data['y'], acc_data['z'],\
            gyr_data['x'], gyr_data['y'], gyr_data['z']))
    '''
    print("ALL DATA: ", sensor.get_all_data())
    '''
    time.sleep(0.1)
