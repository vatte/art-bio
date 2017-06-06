'''
    Electrodermal response detection based on zero crossing

    Valtteri Wikstrom
'''

from numpy import mean
from .DataCollector import DataCollector
import time

class SkinConductance(DataCollector):
    def __init__(self, _Fs, _filter_r, _threshold, _min_length, _min_freq):
        DataCollector.__init__(self, _Fs, _filter_r)

        self.responses = [[]]
        self.found = False

        self.threshold = _threshold
        self.min_length = _min_length
        self.min_freq = _min_freq

    def add_data(self, new_data):
        self.data.extend(new_data)
        l = len(self.filtered_data)

        self.moving_average('data', 'filtered_data', self.filter_r)

        l_resp = len(self.responses)-1

        for i in range(l, len(self.filtered_data)):
            if i > 0:
                d = self.filtered_data[i] - self.filtered_data[i-1]
                if not self.found and d > self.threshold:
                    for j in range(i, 0, -1):
                        #zero-crossing before response
                        if self.filtered_data[j] - self.filtered_data[j-1] < 0:
                            if not self.responses[-1]:
								#and j - self.responses[-2][0] > self.min_freq:
                                self.responses[-1].append(j)
                                self.found = True
                #zero crossing after response
                elif self.found and d < 0:
                    response_l = i - self.responses[-1][0]
                    if response_l > self.min_length:
                        self.responses[-1].append(response_l)
                        self.responses[-1].append(self.filtered_data[i] - self.filtered_data[self.responses[-1][0]])
                        self.responses.append([])
                        #print self.responses[0], self.responses[1], self.responses[2]
                    else:
                        self.responses[-1] = []
                    self.found = False

        l_resp2 = len(self.responses)-1

        return self.responses[l_resp:l_resp2]
