'''
    Python example for gathering ECG and EDA data from bitalino and applying feature extraction

    Valtteri Wikstrom 2017
'''

import glob
import sys
import platform

from bitalino import BITalino # pip install bitalino
from bitalino import find as bitalinoFind

from physiology import HeartRate, SkinConductance

try:
    dev_i = int(float(sys.argv[1]))
except IndexError:
    dev_i = 0

if platform.system() == 'Windows' or platform.system() == 'Linux':
    try:
        bitalinosMacAddress = None
        for mac in bitalinoFind():
            if 'BITalino' in mac[1]:
                print(mac[1])
                bitalinosMacAddress = mac[0]
        print("opening port " + bitalinosMacAddress)
        device_address = bitalinosMacAddress
    except IndexError:
        raise Exception('No BITalino found with index ' + str(dev_i))
else:
    #this is meant for OS X only
    devices = glob.glob('/dev/tty.BITalino*')

    try:
        print("opening port " + devices[dev_i])
        device_address = devices[dev_i]
    except IndexError:
        raise Exception('No BITalino found with index ' + str(dev_i))

chans = [1, 2] # ECG = 1, EDA = 2
fs = 100 # sampling rate
n_samples = 10 # how many samples to read from BITalino

# Connect to BITalino
device = BITalino(device_address)

# Read BITalino version
print(device.version())

# Start Acquisition
device.start(fs, chans)

hr = HeartRate(fs, 32)
edr = SkinConductance(fs, 20, 0.4, 20)

try:
    while True:
        # turn outputs off
        device.trigger([0, 0])

        # Read samples
        in_samples = device.read(n_samples)

        ecg_samples = in_samples[:, -2]
        ibi = hr.add_data(ecg_samples)
        ibis = ibi['ibi']
        for ibi in ibis:
            device.trigger([1, 0])
            print("found heartbeat, length: {} seconds".format(ibi))

        eda_samples = in_samples[:, -1]
        edrr = edr.add_data(eda_samples)
        edrs = edrr['edr']
        for response in edrs:
            print("found edr, length: {} seconds, amplitude: {}".format(float(response[0])/fs, response[1]))
        
except KeyboardInterrupt:
    # Stop acquisition
    device.stop()

    # Close connection
    device.close()
