# OpenBCI Cyton board 8-channel
# a lot of code taken from OpenBCI python library 
# https://github.com/OpenBCI/OpenBCI_Python/blob/master/openbci/cyton.py
# but the library itself is not used since the pip version is broken at the moment https://github.com/OpenBCI/OpenBCI_Python/issues/91
# and since no updates for several months on the issue
# I decided to take the core code from there for now instead of "fixing" the library

import glob
import serial
import serial.tools.list_ports
import struct
import time
import sys

SAMPLE_RATE = 250.0  # Hz
START_BYTE = 0xA0  # start of data packet
END_BYTE = 0xC0  # end of data packet
ADS1299_Vref = 4.5  # reference voltage for ADC in ADS1299.  set by its hardware
ADS1299_gain = 24.0  # assumed gain setting for ADS1299.  set by its Arduino code
scale_fac_uVolts_per_count = ADS1299_Vref / float((pow(2, 23) - 1)) / ADS1299_gain * 1000000.
scale_fac_accel_G_per_count = 0.002 / (pow(2, 4))  # assume set to +/4G, so 2 mG


class OpenBCI():
    #start connection to device
    def __init__(self, dev_i = 0):
        ports = self.list_devices()
        port = ports[dev_i]
        print("Connecting to V3 at port %s" % (port))
        self.ser = serial.Serial(port=port, baudrate=115200)
        self.read_state = 0
        self.data = []

        print("Serial established...")
    


    
    #find all devices
    #return as array of device id strings
    def list_devices(self):
        
        def serial_ports():
            """ Lists serial port names

                :raises EnvironmentError:
                    On unsupported or unknown platforms
                :returns:
                    A list of the serial ports available on the system
            """
        return [comport.device for comport in serial.tools.list_ports.comports()]
        #return glob.glob('/dev/tty.usb*')
    
    #start streaming
    def start(self, fs, channels):
        if(len(channels) != 1 and channels[0] != 'eeg'):
            raise ValueError('OpenBCI only supports eeg channel currently')
        # Initialize 32-bit board, doesn't affect 8bit board
        self.ser.write(b'v')

        # wait for device to be ready
        time.sleep(1)

        #start streaming
        self.ser.write(b'b')

        self.scaling_output = True

        # number of EEG channels per sample *from the board*
        self.eeg_channels_per_sample = 8
        # number of AUX channels per sample *from the board*
        self.aux_channels_per_sample = 3
        self.log_packet_count = 0
        self.packets_dropped = 0
        self.last_sample_time = time.time()


    #read samples (blocking)
    #return as a dict with { chan_name : list_of_samples }
    def read(self):
        # read current sample
        sample = self._read_serial_binary()
        if sample != None:
            return {'eeg': sample}
        return {}

    """
      PARSER:
      Parses incoming data packet into OpenBCISample.
      Incoming Packet Structure:
      Start Byte(1)|Sample ID(1)|Channel Data(24)|Aux Data(6)|End Byte(1)
      0xA0|0-255|8, 3-byte signed ints|3 2-byte signed ints|0xC0
  
    """

    def _read_serial_binary(self, max_bytes_to_skip=3000):
        def read(n):
            bb = self.ser.read(n)
            if not bb:
                print('Device appears to be stalled. Quitting...')
                sys.exit()
            else:
                return bb
        for rep in range(max_bytes_to_skip):
            if self.ser.in_waiting < 100:
                if len(self.data) > 0:
                    copy_data = [d for d in self.data]
                    self.data = []
                    return copy_data
                else:
                    return None
            # ---------Start Byte & ID---------
            if self.read_state == 0:

                b = read(1)

                if struct.unpack('B', b)[0] == START_BYTE:
                    if (rep != 0):
                        print(
                            'Skipped %d bytes before start found' % (rep))
                        rep = 0
                    # packet id goes from 0-255
                    self.packet_id = struct.unpack('B', read(1))[0]
                    self.log_bytes_in = str(self.packet_id)

                    self.read_state = 1

            # ---------Channel Data---------
            elif self.read_state == 1:
                self.channel_data = []
                for _ in range(self.eeg_channels_per_sample):

                    # 3 byte ints
                    literal_read = read(3)

                    unpacked = struct.unpack('3B', literal_read)
                    self.log_bytes_in = self.log_bytes_in + '|' + str(literal_read)

                    # 3byte int in 2s compliment
                    if (unpacked[0] > 127):
                        pre_fix = bytes(bytearray.fromhex('FF'))
                    else:
                        pre_fix = bytes(bytearray.fromhex('00'))

                    literal_read = pre_fix + literal_read

                    # unpack little endian(>) signed integer(i)
                    # (makes unpacking platform independent)
                    myInt = struct.unpack('>i', literal_read)[0]

                    if self.scaling_output:
                        self.channel_data.append(myInt * scale_fac_uVolts_per_count)
                    else:
                        self.channel_data.append(myInt)

                self.read_state = 2

            # ---------Accelerometer Data---------
            elif self.read_state == 2:
                self.aux_data = []
                for _ in range(self.aux_channels_per_sample):

                    # short = h
                    acc = struct.unpack('>h', read(2))[0]
                    self.log_bytes_in = self.log_bytes_in + '|' + str(acc)

                    if self.scaling_output:
                        self.aux_data.append(acc * scale_fac_accel_G_per_count)
                    else:
                        self.aux_data.append(acc)

                self.read_state = 3
            # ---------End Byte---------
            elif self.read_state == 3:
                val = struct.unpack('B', read(1))[0]
                self.log_bytes_in = self.log_bytes_in + '|' + str(val)
                self.read_state = 0  # read next packet
                if (val == END_BYTE):
                    sample = OpenBCISample(self.packet_id, self.channel_data, self.aux_data)
                    self.packets_dropped = 0
                    self.data.append(sample.channel_data)
                    return None
                    #return sample
                else:
                    print("ID:<%d> <Unexpected END_BYTE found <%s> instead of <%s>"
                              % (self.packet_id, val, END_BYTE))
                    print(self.log_bytes_in)
                    self.packets_dropped = self.packets_dropped + 1


    #stop streaming
    def stop(self):
        self.ser.write(b's')
    
    #close connection
    def close(self):
        self.ser.close()

class OpenBCISample(object):
    """Object encapulsating a single sample from the OpenBCI board.
    NB: dummy imp for plugin compatiblity
    """

    def __init__(self, packet_id, channel_data, aux_data):
        self.id = packet_id
        self.channel_data = channel_data
        self.aux_data = aux_data
        self.imp_data = []


if __name__ == "__main__":
    obci = OpenBCI()
    obci.start(250, ['eeg'])

    while True:
        # Read samples
        waiter = obci.ser.in_waiting
        samples = obci.read()
        if samples != {}:
            print(samples)