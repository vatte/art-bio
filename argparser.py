
def getDeviceName(args):
    if '-d' in args or '--device' in args:
        index = next(i for i, arg in enumerate(args) if arg == '-d' or arg == '--device')
        try:
            return args[index+1]
        except IndexError:
            raise ValueError('device name empty')
    return None

def getDeviceIndex(args):
    if '-i' in args or '--index' in args:
        index = next(i for i, arg in enumerate(args) if arg == '-i' or arg == '--index')
        try:
            return int(args[index+1])
        except IndexError:
            raise ValueError('device name empty')
    return None

def getOSCAddress(args):
    if '--osc-address' in args:
        index = next(i for i, arg in enumerate(args) if arg == '--osc-address')
        try:
            return args[index+1]
        except IndexError:
            raise ValueError('OSC address is empty')
    return None

def getOSCPrefix(args):
    if '--osc-prefix' in args:
        index = next(i for i, arg in enumerate(args) if arg == '--osc-prefix')
        try:
            return args[index+1]
        except IndexError:
            raise ValueError('OSC prefix is empty')
    return None

def getSamplingFrequency(args):
    if '--sampling-frequency' in args or '-f' in args:
        index = next(i for i, arg in enumerate(args) if arg == '--sampling-frequency' or arg == '-f')
        try:
            return int(args[index+1])
        except IndexError:
            raise ValueError('sampling frequency is empty')
    return None

def getFilename(args):
    if '--filename' in args:
        index = next(i for i, arg in enumerate(args) if arg == '--filename')
        try:
            return args[index+1]
        except IndexError:
            raise ValueError('filename is empty')
    return None

def getPort(args):
    if '--port' in args:
        index = next(i for i, arg in enumerate(args) if arg == '--port')
        try:
            return args[index+1]
        except IndexError:
            raise ValueError('port is empty')
    return None


source_types = ['ecg', 'eda', 'eeg', 'emg']
destination_types = ['osc', 'file', 'digital', 'ws']

def getConnections(args):

    connection_indexes = [x for x in range(0, len(args)) if args[x] == '-c' or args[x] == '--connect']

    connections = {}

    for i in connection_indexes:
        try:
            source = args[i+1]
            destination = args[i+2]
        except IndexError:
            raise ValueError('missing argument(s) for --connect command')
        if not source in source_types:
            if not (source[0] == 'r' and source[1:] in source_types):
                raise ValueError(source + ' is not a valid source')
        if not destination in destination_types:
            raise ValueError(destination + ' is not a valid destination')
        
        print( 'Connection: ' + source + ' to ' + destination )

        if not source in connections:
            # add source type to connections dictionary
            connections[source] = []
        
        if not destination in connections[source]:
            connections[source].append(destination)
    
    return connections
