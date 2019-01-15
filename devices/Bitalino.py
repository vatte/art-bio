# Bitalino (r)evolution BT

import glob
import sys
import platform
import time
from threading import Thread

import bitalino # windows and linux need pybluez to be installed
                # pip install bitalino


from .Device import Device

class Bitalino(Device):

    def __init__(self, dev_i = 0):
        #start connection to device

        #channel numbers for bitalino
        self.channel_map = {
            'emg': 0,
            'ecg': 1,
            'eda': 2,
            'eeg': 3,
            'acc': 4,
            'lux': 5
        }
        self.digital_triggers = [1, 1]

        # find device
        self.device_list = self.list_devices()
        try:
            device_address = self.device_list[dev_i]
        except IndexError:
            raise Exception('No BITalino found with index ' + str(dev_i))

        print("Connecting to " + device_address)
        
        # Connect to BITalino
        self.device = bitalino.BITalino(device_address)
        # Read BITalino version
        print(self.device.version())
    
    #find all devices
    def list_devices(self):
        devices = []
        if platform.system() == 'Windows' or platform.system() == 'Linux':
            for mac in bitalino.find():
                if 'BITalino' in mac[1]:
                    devices.append(mac[0])
        else: #this is meant for OS X only
            devices = glob.glob('/dev/tty.BITalino*')
        return devices
    
    #start streaming
    def start(self, fs, channels):
        self.fs = fs
        self.channels = []
        chans = []
        #order channels for bitalino 
        for c in self.channel_map.keys():
            if c in channels:
                self.channels.append(c)
                chans.append(self.channel_map[c])
        # Start Acquisition
        self.device.start(fs, chans)
        self.started = True

    #read samples (blocking)
    def read(self):
        in_samples = self.device.read(round(self.fs / 10))
        samples = {}
        for i, c in enumerate(self.channels):
            samples[c] = in_samples[:, -len(self.channels) + i].tolist()
            if c == 'eeg': #eeg supports multiple electrodes
                samples[c] = [samples[c]]
        return samples

    #stop streaming
    def stop(self):
        # Stop acquisition
        self.device.stop()
        self.started = False

    #close connection
    def close(self):
        if self.started:
            self.stop()        
        # Close connection
        self.device.close()
    
    #toggle bitalino digital outputs, format [int, int]
    def digital_trigger(self):
        print('triggering digital')
        def myfunc(i):
            self.device.trigger(self.digital_triggers)
            time.sleep(0.1)
            self.device.trigger([0, 0])

        
        t = Thread(target=myfunc, args=(i,))
        t.start()

