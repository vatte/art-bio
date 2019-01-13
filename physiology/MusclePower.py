import numpy as np

from .DataCollector import DataCollector

class MusclePower(DataCollector):
    def __init__(self, _Fs):
        DataCollector.__init__(self, _Fs)
        self.avg = -1
    
    def add_data(self, new_data):
        if self.avg == -1:
            self.avg = np.mean(new_data)
        else:
            self.avg = 0.9 * self.avg + 0.1 * np.mean(new_data)

        emg_power = np.mean(np.abs(new_data - self.avg))

        return {'power': [emg_power]}
