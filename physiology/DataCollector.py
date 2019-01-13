'''
    Generic datacollector class for physiological signals

    Valtteri Wikstrom
'''

import time

class DataCollector:

    def __init__(self, _Fs):
        self.Fs = _Fs
        self.data = []
        self.filtered_data = []

    def add_data(self, data):
        return {'feature': []} #return features
        
    def mean(self, numbers):
        total = 0
        for number in numbers:
            total += number
        return total / len(numbers)

    def moving_average(self, data, filtered_data, filter_r):
        if len(vars(self)[data]) > filter_r*2+1:
            if len(vars(self)[filtered_data]) <= filter_r:
                vars(self)[filtered_data][:] = []
                vars(self)[filtered_data] = [self.mean(vars(self)[data][0:2*filter_r+1])]*(filter_r+1)
            for i in range(len(vars(self)[filtered_data]), len(vars(self)[data])-filter_r-1):
                vars(self)[filtered_data].append(self.mean(vars(self)[data][i-filter_r:i+filter_r+1]))

