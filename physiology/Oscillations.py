import numpy as np

class Oscillations:
    def __init__(self, sample_rate, fft_size, overlap, freqs):
        self.idx = 0
        self.sample_rate = sample_rate
        self.fft_size = fft_size
        self.overlap = overlap
        self.hanning = np.hanning(fft_size)
        self.pad = np.zeros(fft_size)
        self.freqs = freqs
        self.spectdata = np.zeros(fft_size)

    def add_data(self, samples):
        freqs = None
        for i in range(len(samples)):
            freqs_in = self.add_sample(samples[i])
            #freqs = freqs_in if freqs_in != None else freqs
            if freqs_in != None:
                if freqs == None:
                    freqs = {}
                    for freq in freqs_in:
                        freqs[freq] = [freqs_in[freq]]
                else:
                    for freq in freqs_in:
                        freqs[freq].append(freqs_in[freq])

        return freqs
    
    def add_sample(self, sample):
        self.spectdata[self.idx] = sample
        self.idx += 1
        if self.idx >= self.fft_size:
            #result = [[] for i in range(self.num_chans)]
            freqpower = {}
            for f in self.freqs:
                freqpower[f] = 0
            #raw_electrode = []
            windowed = self.spectdata * self.hanning
            padded = np.append(windowed, self.pad)
            spectrum = np.fft.fft(padded)
            autopower = abs(spectrum * np.conj(spectrum)) 
            result = autopower[:self.fft_size]
            
            powerspect = 10.0 * np.log10(np.power(abs(spectrum),2))
            freqC = np.fft.fftfreq(len(padded), 1.0/self.sample_rate)
            
            for f in self.freqs:
                freq = self.freqs[f]
                start = np.where((freqC <= freq[0]) & (freqC >= 0))[0][-1]
                stop = np.where((freqC >= freq[1]) & (freqC >= 0))[0][0]
                freqpower[f] = np.mean(powerspect[start:stop]) + np.mean(powerspect[-stop-1:-start-1])
            
            self.idx = int(self.fft_size * self.overlap)
            #raw_electrode = [float(self.spectdata[a]) for a in range(self.idx, len(self.spectdata))]
            if self.idx > 0:
                self.spectdata[:self.idx] = self.spectdata[-self.idx:]
                    
            return freqpower
        return None
