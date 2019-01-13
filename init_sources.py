from physiology import HeartRate, SkinConductance, Oscillations, DataCollector, MusclePower

import parser

# initialize sources for feature extraction
def init_sources(connections, fs):
    sources = {}

    for source in connections.keys():
        if source[0] == 'r' and source[1:] in parser.source_types:
            source = source[1:]
        if not source in sources:
            if source == 'ecg':
                sources[source] = HeartRate(fs, 32)
            elif source == 'eda':
                sources[source] = SkinConductance(fs, 20, 0.4, 20)
            elif source == 'emg':
                sources[source] = MusclePower(fs)
            elif source == 'eeg':
                sources[source] = Oscillations(fs, 1, 500, 0.75, 
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