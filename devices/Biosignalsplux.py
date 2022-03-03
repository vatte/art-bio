# biosignalsplux

import glob
import sys
import platform
import time

from threading import Thread

sys.path.append('devices/pluxlib') #add the plux library for your platform to this folder
import plux

from .Device import Device

class Biosignalsplux(Device):

    def __init__(self, dev_i = 0):

        #default channel numbers for biosignalsplux
        self.channel_map = {
            'emg': [0],
            'ecg': [1],
            'eda': [2],
            'eeg': [3]
        }

        # find device
        print('Looking for biosignalsplux device')
        retries = 0
        self.device_list = []

        while retries < 3 and len(self.device_list) == 0:
            self.device_list = self.list_devices()
        
        if len(self.device_list) == 0:
            raise Exception('No biosignalsplux device found')

        try:
            device_address = self.device_list[dev_i]
        except IndexError:
            raise Exception('No biosignalsplux found with index ' + str(dev_i))

        print("Connecting to " + device_address)

        class PluxDevice(plux.SignalsDev):
            def __init__(self, address):
                plux.MemoryDev.__init__(address)
                self.started = True
                self.in_samples = []

            def onRawFrame(self, nSeq, data):  # onRawFrame takes three arguments
                self.in_samples.append(data)
                if not self.started:
                    return True
                return False
        
        # Connect to biosignalsplux
        self.device = PluxDevice(device_address)
    
    #find all devices
    def list_devices(self):
        devices = []
        for mac in plux.BaseDev.findDevices():
            devices.append(mac[0])
        return devices
    
    #start streaming
    def start(self, fs, channels):
        self.fs = fs
        self.channels = []
        chans = []
        #order channels for biosignalsplux 
        for c in self.channel_map.keys():
            if c in channels:
                for index in self.channel_map[c]:
                    chans.append(index)
        chans.sort()
        self.n_chans = chans[-1] + 1
        for c in range(self.n_chans):
            found = False
            for k in self.channel_map:
                if c in self.channel_map[k]:
                    self.channels.append(k)
                    found = True
                    break
            if not found:
                self.channels.append('unknown')
        print(self.channels)

        codes = [ 0x01, 0x03, 0x07, 0x0F, 0x1F, 0x3F, 0x7F, 0xFF] #codes for biosignalsplux device for different n_chans

        # Start Acquisition
        self.started = True
        self.device.started = True
        self.device.start(fs, codes[self.n_chans-1], 16)

        def myfunc():
            self.device.loop()

        t = Thread(target=myfunc)
        t.start()

    

    #read samples (blocking)
    def read(self):
        samples = {}

        while len(self.device.in_samples) == 0:
            time.sleep(0.01)

        for i, c in enumerate(self.channels):
            if not c in samples:
                samples[c] = []
            samples[c].append([s[i] for s in self.device.in_samples])
        #if 'eeg' in samples:
        #    samples['eeg'] = [ [ [samples['eeg'][i][j] for i in range(len(samples['eeg'])) ] for j in range(len(samples['eeg'][0]))] ]
        #print(samples)
        self.device.in_samples = [] # clear the sample buffer
        return samples

    #stop streaming
    def stop(self):
        # Stop acquisition
        self.started = False
        self.device.started = False

    #close connection
    def close(self):
        if self.started:
            self.started = False
            self.device.started = False
    