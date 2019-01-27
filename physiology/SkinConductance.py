'''
    Electrodermal response detection based on zero crossing
        response format [length, amplitude]
    
    Valtteri Wikstrom
'''

from .DataCollector import DataCollector
import time

class SkinConductance(DataCollector):
    def __init__(self, _Fs, _filter_r, _threshold, _min_length):
        DataCollector.__init__(self, _Fs)
        self.filter_r = _filter_r

        self.responses = [[]]
        self.found = False

        self.threshold = _threshold
        self.min_length = _min_length # in samples

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
                                self.responses[-1].append(j)
                                self.found = True
                                break
                #zero crossing after response
                elif self.found and d < 0:
                    response_l = i - self.responses[-1][0]
                    if response_l > self.min_length:
                        self.responses[-1][0] = response_l
                        self.responses[-1].append(self.filtered_data[i] - self.filtered_data[i-response_l])
                        self.responses.append([])
                    else:
                        self.responses[-1] = []
                    self.found = False

        l_resp2 = len(self.responses)-1

        return {'edr': self.responses[l_resp:l_resp2]}

