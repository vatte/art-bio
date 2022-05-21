'''
    ECG signal beat detection based on algorithm described in:
	Christov: "Real time electrocardiogram QRS detection using combined adaptive threshold"

    Valtteri Wikstrom
'''

from .DataCollector import DataCollector

class HeartRate(DataCollector):
    
    def __init__(self, _Fs, _filter_r):
        self.filter_r = _filter_r
        self.Fs = _Fs
        self.initialize()

    
    def initialize(self):
        DataCollector.__init__(self, self.Fs)

        #todo: stores unnecessarily all the previous data

        self.clead = []
        self.filtered_clead = []
        self.emg_filter_r = int(0.5*self.Fs/34)
        self.clead_filter_r = int(0.5*self.Fs/24)
        
        self.initialized = False
        self.init_time = 5
        
        self.beats = []
        self.last = 0
        self.detect_interval = int(0.2*self.Fs)
        
        self.r = 0
        self.rr = 0
        self.RR = [0, 0, 0, 0, 0]
        self.r_i = -1
        
        self.f_interval = int(self.Fs*0.35)
        self.f_interval2 = int(self.Fs*0.05)
    
    def add_data(self, new_data):
        self.data.extend(new_data)
        
        #no powerline filtering because nexus is battery powered
        #emg filtering
        self.moving_average('data', 'filtered_data', self.emg_filter_r)
        
        #'complex' lead is made here, but for now just one lead
        if len(self.filtered_data) > 3 and len(self.filtered_data) > len(self.clead) + 1:
            for i in range(len(self.clead), len(self.filtered_data) - 1):
                if i==0:
                    self.clead.append(abs(self.filtered_data[2] - self.filtered_data[0]))
                else:
                    self.clead.append(abs(self.filtered_data[i-1] - self.filtered_data[i+1]))
        
        last_clead_i = len(self.filtered_clead)
        #complex lead amplified noise filtering
        self.moving_average('clead', 'filtered_clead', self.clead_filter_r)
        
        ibis = []
        if not self.initialized and len(self.filtered_clead) > self.init_time * self.Fs:
            self.init_beats()
            ibis = self.detect_beats(0)
        elif self.initialized:
            ibis = self.detect_beats(last_clead_i)
        
        #if len(ibis) > 0:
        #    print(ibis)
        
        #reinitialize if no beats are detected for duration of self.init_time
        if len(self.filtered_clead) - self.last > self.init_time * self.Fs:
            print('re-initializing...')
            self.initialize()
            print(len(self.filtered_clead), self.last)

        return {'ibi': ibis}
        
        
    def init_beats(self):
        self.initialized = True
        
        #initialize M 
        self.m = 0.6*max(self.filtered_clead[0:self.Fs*self.init_time])
        self.M = [self.m, self.m, self.m, self.m, self.m]
        self.m_i = 0
        self.m_d = (self.m*0.4)/self.Fs
        
        #initialise f 
        self.f = self.mean(self.filtered_clead[0:self.f_interval])
        
    def detect_beats(self, last_i):
        new_beats = []
        
        for i in range(last_i, len(self.filtered_clead)):
            #calculate f-value
            if i > self.f_interval:
                self.f = self.f+(max(self.filtered_clead[i-self.f_interval2:i]) - max(self.filtered_clead[i - self.f_interval : i - self.f_interval + self.f_interval2])) / 150
                
            #calculate r-value
            if i < self.rr/3 + self.last:
                self.r = 0
            elif self.r_i > 0 and i < self.last + self.rr:
                self.r = self.r - self.m_d/1.4
            
            if i - self.last >= self.detect_interval:
                if i - self.last == self.detect_interval: # update M
                    new_M = 0.6*max(self.filtered_clead[self.last : i])
                    old_M = self.M[self.m_i]
                    self.m_i = (self.m_i + 1) % len(self.M)
                    if new_M > 1.5*self.M[self.m_i]:
                        self.M[self.m_i] = 1.1 * old_M
                    else:
                        self.M[self.m_i] = new_M
                        
                    self.m = self.mean(self.M)
                    
                    self.m_d = 0.4 * self.m / self.Fs
                
                elif i - self.last <= 1.2 * self.Fs: #lower slope upto 1.2 s
                    self.m = self.m - self.m_d

                if self.filtered_clead[i] > self.m + self.f + self.r: # found beat
                    #print i - self.last
                    if self.r_i == -1 and not self.last == 0: # init R
                        self.RR = [ i-self.last, i-self.last, i-self.last, i-self.last, i-self.last ]
                        self.r_i = 0
                    else:
                        self.RR[self.r_i] = i-self.last
                        self.r_i = (self.r_i + 1) % 5
                    self.rr = self.mean(self.RR)
    
                    self.beats.append(i)
                    new_beats.append((i - self.last) / float(self.Fs))
                    self.last = i
        
        return new_beats
        
