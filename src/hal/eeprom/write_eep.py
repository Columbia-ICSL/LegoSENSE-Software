import time
from eep_util import EEP

eep = EEP()
time.sleep(0.1)

if __name__ == "__main__":
    while True:
        try:
            available_slots = [i+1 for i, x in enumerate(eep.get_status()[0]) if x]
            if len(available_slots):
                print(f'Available slots: {available_slots}')
                idx = int(input('Select a slot to program: '))
                if idx in available_slots:
                    data = eep.read_eep(idx)
                    if data is not None:
                        print(f'Slot {idx} has {len(data)} bytes of data: {data}')
                    else:
                        print(f'Slot {idx} has an empty EEPROM!')
                    to_write = input('Input data to write: ')
                    if len(to_write) == 0:
                        print("Nothing written")
                    else:
                        eep.write_eep(idx, to_write)
                    print('OK\n')
                else:
                    print(f"Slot {idx} not available!")
                    continue
            else:
                print('No slots available! Retrying in 1 sec ...')
                time.sleep(1)
        except KeyboardInterrupt:
            break