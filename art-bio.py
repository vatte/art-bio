# coding=UTF-8
readme = '''
 🐍 rt-bio : A Real-Time BIOsignal feature extraction tool 🦆 
    https://github.com/vatte/rt-bio

    sources:
        ecg (electrocardiogram) sends /ecg/ibi
        recg (same as above + /ecg/raw)
        eeg (electroencephalogram sends /eeg/alpha, /eeg/beta /eeg/gamma, /eeg/theta)
        reeg (same as above + /eeg/raw)
        emg (electromyogram) sends /emg/power
        remg (same as above + /emg/raw)
        eda (electrodermal activity) sends /eda/edr([length, amplitude])
        reda (same as above + /eda/raw)

        example usage:
            art-bio -c ecg osc -c reeg file

    command line arguments:
    -d, --device [device_type (default: bitalino)]
        choose biosignal acquisition device
        [device_type] - bitalino, (openbci soon i promise...)
    -f, --freq [sampling_frequency (default: 100)]
        set sampling frequency for biosignal data acquisition
    -l, --list
        lists available devices
    -i, --index [device_index (default: 0)]
        set the correct device from available devices, see --list
    -c, --connect [sourcetype] [destinationtype] 
        makes connections for biosignal sources to data destinations
        [source]: ecg, eda, eeg, emg
        [destination]: osc, file, digital
    --osc-address [destination_address]
        [destination_address (default: 127.0.0.1:4810)] IP_ADDRESS:PORT
    --osc-prefix [prefix]
        [prefix (default: /rtbio)]
    --filename [filename]
        [filename (default: temp.txt)]
'''

import sys
import configparser

import argparser as parser
from devices import *
from devices.Biosignalsplux import Biosignalsplux
from init_sources import init_sources
from router import Router


print("art-bio - A Real-Time BIOsignal feature extraction tool")


router = Router()

#set default argument values
device_name = 'bitalino'
sampling_frequency = 100
device_index = 0
router.osc_address = '127.0.0.1:4810'
router.osc_prefix = '/rtbio'
router.filename = 'temp.txt'
router.ws_port = 5678

args = sys.argv

#get devicename from args
device_name_arg = parser.getDeviceName(args)
if device_name_arg:
    device_name = device_name_arg

#get device index from args
device_index_arg = parser.getDeviceIndex(args)
if device_index_arg:
    device_index = device_index_arg

#list devices and exit if --list
if '-l' in args or '--list' in args:
    print('list of ' + device_name + ' devices: ')
    if(device_name == 'bitalino'):
        device_list = Bitalino.list_devices(None)
        for i, dev in enumerate(device_list):
            print('[{}] {}'.format(i, dev))
    elif(device_name == 'openbci'):
        device_list = OpenBCI.list_devices(None)
        for i, dev in enumerate(device_list):
            print('[{}] {}'.format(i, dev))
    elif(device_name == 'biosignalsplux'):
        device_list = Biosignalsplux.list_devices(None)
        for i, dev in enumerate(device_list):
            print('[{}] {}'.format(i, dev))
    else:
        raise ValueError('No such device: ' + device_name)
    print('exiting...')
    sys.exit(0)

#get osc_address from args
osc_address_arg = parser.getOSCAddress(args)
if osc_address_arg:
    router.osc_address = osc_address_arg

#get osc_prefix from args
osc_prefix_arg = parser.getOSCPrefix(args)
if osc_prefix_arg:
    router.osc_prefix = osc_prefix_arg

#get filename from args
filename_arg = parser.getFilename(args)
if filename_arg:
    router.filename = filename_arg

#get ws port from args
port_arg = parser.getPort(args)
if port_arg:
    router.ws_port = port_arg


#get sampling_frequency from args
sampling_frequency_arg = parser.getSamplingFrequency(args)
if sampling_frequency_arg:
    sampling_frequency = sampling_frequency_arg

#get connections from args
connections = parser.getConnections(args)

#if no connections set show help
if not len(connections):
    print(readme)
    sys.exit(0)

#read config file if it exists
config = configparser.ConfigParser()
config.read('config.ini')

#initialize device
if device_name == 'bitalino':
    device = Bitalino(device_index)
    if 'bitalino' in config:
        channels = {}
        for k in config['bitalino']:
            channels[k] = [ int(c) for c in config['bitalino'][k].split(',') ]
        device.channel_map = channels
    router.digital_out_func = device.digital_trigger
elif device_name == 'openbci':
    device = OpenBCI(device_index)
    def noDigital():
        raise ValueError('openbci has no digital output defined')
    router.digital_out_func = noDigital
elif device_name == 'biosignalsplux':
    device = Biosignalsplux(device_index)
    if 'biosignalsplux' in config:
        channels = {}
        for k in config['biosignalsplux']:
            channels[k] = [ int(c) for c in config['biosignalsplux'][k].split(',') ]
        device.channel_map = channels

else:
    raise ValueError('No such device: ' + device_name)


#initialize sources and destinations
sources = init_sources(connections, device.channel_map, sampling_frequency)
router.init_destinations(connections)

#start streaming
device.start(sampling_frequency, sources.keys())

## filter experiment here for powerline
# from scipy import signal

# b,a = signal.iirnotch(50, 25, 100)

# print("B: " + str(b) + "A: " + str(a))

# z = [0, 0, 0, 0, 0, 0, 0, 0]
# for i, zz in enumerate(z):
#     z[i] = signal.lfilter_zi(b, a)

try:
    while True:
        # Read samples
        samples = device.read()
        #print(samples)
        for source in samples.keys():
            features = []
            for i, channel in enumerate(samples[source]):
                #for j, s in enumerate(channel):
                    #y, z[i] = signal.lfilter(b,a,[s], zi = z[i])
                    #channel[j] = y[0]
                if source != 'unknown' and source in sources:
                    features.append(sources[source][i].add_data(channel))
            router.route_data(source, connections, features, samples[source])

except (Exception, KeyboardInterrupt) as e:
    device.close()
    if router.ws_server:
        router.ws_server.stop()
    raise(e)
