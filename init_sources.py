from physiology import HeartRate, SkinConductance, Oscillations, DataCollector, MusclePower

import argparser as parser

# initialize sources for feature extraction
def init_sources(connections, fs):
    sources = {}

    for source in connections.keys():
        if source[0] == 'r' and source[1:] in parser.source_types:
            source = source[1:]
        if source in parser.source_types and not source in sources:
            if source == 'ecg':
                sources[source] = HeartRate(fs, 20)
            elif source == 'eda':
                sources[source] = SkinConductance(fs, 200, 0.05, 30)
            elif source == 'emg':
                sources[source] = MusclePower(fs)
            elif source == 'eeg':
                #have to get eeg chan numbers from somewhere
                num_chans = 1 if fs == 100 else 8
                print('number of chans {}'.format(num_chans))
                sources[source] = Oscillations(fs, num_chans, 500, 0.75, 
                    {
                        'theta': [4.0, 8.0],
                        'alpha': [8.0, 13.0],
                        'beta': [13.0, 30.0],
                        'delta': [3.0, 4.0],
                    }
                )
            else:
                sources[source] = DataCollector(fs)
    return sources