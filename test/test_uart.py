import time
import serial
import random

rand = random.Random()


def test_uart(test_dev):
    '''Echo test for uart addressed at <test_dev>'''
    def get_random_bytes(size):
        result = bytearray(size)
        for i in range(size):
            result[i] = rand.randint(0, 255)
        return result

    with serial.Serial(test_dev, 115200, timeout=1) as ser:
        """
        Examples:
        ser.write(<bytearray>)  # write the bytearray
        x = ser.read()          # read one byte
        x = ser.read(10)        # read 10 bytes
        line = ser.readline()   # read a '\n' terminated line
        """
        test_size = rand.randint(1, 10)
        test_buf = get_random_bytes(test_size)
        
        ser.write(test_buf)
        s = ser.read(test_size)
        if(s != test_buf):
            print(f'[ERROR] UART {test_dev}\n\tEXPECTED >>{test_buf}<<\n\tRECEIVED >>{s}<<')
            return False
        else:
            print(f'[OK] UART {test_dev}')
            return True


if __name__ == '__main__':
    # uart0 = '/dev/ttyAMA0'
    uart1 = '/dev/ttyS0'
    uart2 = '/dev/ttyAMA1'  
    uart3 = '/dev/ttyAMA2'  # module 3
    uart4 = '/dev/ttyAMA3'  # module 4
    # uart5 = '/dev/ttyAMA4'
    
    for dev in [uart1, uart2, uart3, uart4]:
        test_uart(dev)
