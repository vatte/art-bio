import time
import numpy as np
import sys
from threading import Thread

from physiology import Oscillations

sample_rate = 250
num_chans = 2
sample_time = 1./sample_rate
fft_size = 1000
overlap = 0.75
freqs = {
    'alpha': [8.0, 13.0],
    'all': [1, 40]
}

normalization_length = int(60 * sample_rate / fft_size / (1 - overlap)) #data points
normalizer = []
normalizer_index = 0

def normalize_all(data, normalizer):
    normalized = {}
    for d in ['alpha', 'lateralization']:
        d_data = [normalizer[i][d] for i in xrange(len(normalizer))]
        normalized[d] = normalize(data[d], d_data)
    return normalized

def normalize(num, data):
    mean = np.median(data)
    std = np.std(data)
    minimum = mean - 2*std
    maximum = mean + 2*std
    try:
        return min(1, max(0, float((num - minimum) / (maximum - minimum))))
    except:
        return 0



def cb_func(data):
    global normalizer_index
    freqpower = data['freqpower']
    for k in freqpower:
        for i,e in enumerate(freqpower[k]):
            if ~np.isfinite(freqpower[k][i][0]):
                freqpower[k][i][0] = 0
    out_data = {}
    out_data['alpha'] = np.mean(freqpower['alpha'][0:1])
    out_data['lateralization'] = (freqpower['alpha'][0]) - (freqpower['alpha'][1])

    print(freqpower['all'])
    
    if True: #np.mean(freqpower['all']) > 0:

        if len(normalizer) < normalization_length:
            #calibrating: don't send data
            normalizer.append(out_data)
            send_json({'status': 'calibrating'})
        else:
            #normal operation
            normalizer[normalizer_index] = out_data
            normalizer_index = (normalizer_index + 1) % normalization_length

            normaled = normalize_all(out_data, normalizer)
            normaled['timestamp'] = time.time()
            normaled['status'] = 'normal'
            send_json(normaled)
        send_local_json(data['raw'])

def send_json(data):
    print(data)

    #data['user_id'] = user_id
    #print("sending data " + data['status'] + " " + str(time.time()))
    #socketIO.emit('eeg', data)

def send_local_json(data):
    print(data)
    #socketIO.emit('raweeg', {'data': data, 'user_id': user_id})

oscillations = Oscillations(sample_rate, num_chans, fft_size, overlap, freqs)


import glob
import serial
import struct


def bytesTo24bitInt(bs):
    if (ord(bs[0]) >= 127):
        prefix = bytes(bytearray.fromhex('FF')) 
    else:
        prefix = bytes(bytearray.fromhex('00'))
    prefixed = str(prefix) + str(bs)
    num = struct.unpack('>i', prefixed)[0]
    return num

ports = glob.glob('/dev/tty.usb*')

print("opening serial port " + ports[0])

ser = serial.Serial(port=ports[0],baudrate='115200', timeout=5)

print("open")

print("starting openbci")
ser.write(b'v')

line = ''
lines = 0
while line != b'$$$' and lines < 8:
    line = ser.readline()
    print(line)
    lines += 1

print("configuring openbci")
time.sleep(1)
# turn off unneeded chans
ser.write(b'3')
ser.write(b'4')
ser.write(b'5')
ser.write(b'6')
ser.write(b'7')
ser.write(b'8')

#ser.write(b'x2040000X') # channel 2 set for ekg
time.sleep(1)

print("turning on streaming")
ser.write(b'b')

print("begin processing")


while True:
    c = ser.read()
    if c is chr(0xA0):
        line = ''
        while True:
            c = ser.read()
            if c is chr(0xC0):
                break
            else:
                line += c
        if len(line) == 31:
            samples = []
            for i in xrange(2):
                samples.append(bytesTo24bitInt(line[(1+i*3):(4+i*3)]))
            samples = np.array(samples) * 4.5 / 24 / (2^23 - 1)
            oscillations.add_samples(samples)
    elif c is not "":
        pass


ser.write(b's') #stop streaming


