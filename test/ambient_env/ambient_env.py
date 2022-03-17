import time
from AHT20 import AHT20
from SPL06 import SPL06

temp_hum = AHT20()
pressure = SPL06()

while True:
    print("{:10.2f}".format(temp_hum.get_humidity()) + " %RH" + "{:10.2f}".format(temp_hum.get_temperature()) + " °C"
          + "{:10.2f}".format(pressure.get_pressure()) + " mb")
    time.sleep(0.1)
