from physiology import HeartRate, SkinConductance, Oscillations, DataCollector, MusclePower

import argparser as parser

# initialize sources for feature extraction
def init_sources(connections, channel_map, fs):
    sources = {}

    for source in connections.keys():
        if source[0] == 'r' and source[1:] in parser.source_types:
            source = source[1:]
        if source in parser.source_types and not source in sources:
            sources[source] = []
            for _ in channel_map[source]:
                if source == 'ecg':
                    sources[source].append(HeartRate(fs, 20))
                elif source == 'eda':
                    sources[source].append(SkinConductance(fs, 200, 0.05, 30))
                elif source == 'emg':
                    sources[source].append(MusclePower(fs))
                elif source == 'eeg':
                    #have to get eeg chan numbers from somewhere FIX THIS
                    num_chans = 1 if fs == 100 else 8
                    print('number of chans {}'.format(num_chans))
                    sources[source].append(Oscillations(fs, num_chans, 256, 0.8, 
                        {
                            'theta': [4.0, 8.0],
                            'alpha': [8.0, 13.0],
                            'beta': [13.0, 30.0],
                            'delta': [1.0, 4.0],
                        }
                    ))
                else:
                    sources[source].append(DataCollector(fs))
    return sources