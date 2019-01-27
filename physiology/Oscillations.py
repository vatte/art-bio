import numpy as np

class Oscillations:
    def __init__(self, sample_rate, num_chans, fft_size, overlap, freqs):
        self.idx = 0
        self.sample_rate = sample_rate
        self.num_chans = num_chans
        self.fft_size = fft_size
        self.overlap = overlap
        self.hanning = np.hanning(fft_size)
        self.pad = np.zeros(fft_size)
        self.freqs = freqs
        self.spectdata = [np.zeros(fft_size) for _ in range(num_chans)]

    def add_data(self, samples):
        freqs = None
        for i in range(len(samples[0])):
            out = []
            for c in samples:
                out.append(c[i])
            freqs = self.add_samples(out)
        return freqs
    
    def add_samples(self, samples):
        for i, sample in enumerate(samples):
            self.spectdata[i][self.idx] = sample
        self.idx += 1
        if self.idx >= self.fft_size:
            result = [[] for i in range(6)]
            freqpower = {}
            for f in self.freqs:
                freqpower[f] = [0 for _ in range(len(samples))]
            raw_electrodes = [[] for _ in range(len(self.spectdata))]
            for i, electrode_data in enumerate(self.spectdata):
                windowed = electrode_data * self.hanning
                padded = np.append(windowed, self.pad)
                spectrum = np.fft.fft(padded)
                autopower = abs(spectrum * np.conj(spectrum)) 
                result[i] = autopower[:self.fft_size]
                
                powerspect = 10.0 * np.log10(np.power(abs(spectrum),2))
                freqC = np.fft.fftfreq(len(padded), 1.0/self.sample_rate)
                
                for f in self.freqs:
                    freq = self.freqs[f]
                    start = np.where((freqC <= freq[0]) & (freqC >= 0))[0][-1]
                    stop = np.where((freqC >= freq[1]) & (freqC >= 0))[0][-1]
                    freqpower[f][i] = sum(powerspect[start:stop])            
                
                self.idx = int(self.fft_size * self.overlap)
                raw_electrodes[i] = [float(electrode_data[a]) for a in range(self.idx, len(electrode_data))]
                if self.idx > 0:
                    electrode_data[:self.idx] = electrode_data[-self.idx:]
                    
            return freqpower
        return None
