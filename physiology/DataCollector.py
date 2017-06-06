'''
    Generic datacollector class for physiological signal

    Valtteri Wikstrom
'''

from numpy import mean
import time

class DataCollector:

    def __init__(self, _Fs, _filter_r):
        self.Fs = _Fs
        self.data = []
        self.filtered_data = []
        self.filter_r = _filter_r
        
    def moving_average(self, data, filtered_data, filter_r):
        if len(vars(self)[data]) > filter_r*2+1:
            if len(vars(self)[filtered_data]) <= filter_r:
                vars(self)[filtered_data][:] = []
                vars(self)[filtered_data] = [mean(vars(self)[data][0:2*filter_r+1])]*(filter_r+1)
            for i in range(len(vars(self)[filtered_data]), len(vars(self)[data])-filter_r-1):
                vars(self)[filtered_data].append(mean(vars(self)[data][i-filter_r:i+filter_r+1]))

