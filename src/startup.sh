#!/bin/bash
INTERNET_OK=true
printf "%s" "Waiting for Internet ..."
while ! ping -c 1 -n -w 1 1.1.1.1 &> /dev/null
do
    sleep 1
    printf "\nWaiting ... %ds" "$SECONDS"
    if [[ $SECONDS -gt 300 ]]; then
        printf "\n%s\n" "Timed out waiting for Internet"
        INTERNET_OK=false
        break
    fi
done
if [ "$INTERNET_OK" = true ] ; then
    printf "\n%s\n"  "System is online. Waiting for time sync..."
    # Wait for time sync
    sleep 10
    printf "$s\n" "Starting services"
fi

/usr/bin/screen -dmS sensorhub_controller bash -c '/home/pi/workspace/env/shenv/bin/python /home/pi/workspace/SensorHub/src/controller/controller.py; exec bash'
/usr/bin/screen -dmS sensorhub_service bash -c '/home/pi/workspace/env/shenv/bin/python /home/pi/workspace/SensorHub/src/sehd.py /home/pi/workspace/SensorHub/src/fuse; exec bash'
/usr/bin/screen -dmS frp bash -c '/home/pi/workspace/frp/frpc -c /home/pi/workspace/frp/frpc.ini; exec bash'
