import time
from eep_util import EEP

eep = EEP()
time.sleep(0.1)

if __name__ == "__main__":
    while True:
        try:
            available_slots = [i+1 for i, x in enumerate(eep.get_status()) if x]
            if len(available_slots):
                print(f'Available slots: {available_slots}')
                idx = int(input('Select a slot to program: '))
                if idx in available_slots:
                    data = eep.read_eep(idx)
                    print(f'Slot {idx} has {len(data)} bytes of data: {data}')
                    to_write = input('Input data to write: ')
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