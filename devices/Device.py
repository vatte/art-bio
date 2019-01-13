# Generic Device

class Device():
    #start connection to device
    def __init__(self, dev_i = 0):
        pass
    
    #find all devices
    #return as array of device id strings
    def list_devices(self):
        return []
    
    #start streaming
    def start(self, fs, channels):
        pass

    #read samples (blocking)
    #return as a dict with { chan_name : list_of_samples }
    def read(self):
        return {}

    #stop streaming
    def stop(self):
        pass
    
    #close connection
    def close(self):
        pass
