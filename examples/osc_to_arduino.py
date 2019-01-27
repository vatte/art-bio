import sys
import serial

from pythonosc import dispatcher
from pythonosc import osc_server

ser = None

def ecg_receive(address, value):
    print('BEAT! ' + str(value))
    ser.write(b'B')


if __name__ == "__main__":
    try:
        port = sys.argv[1]
        ser = serial.Serial(port)

        dispatcher = dispatcher.Dispatcher()
        dispatcher.map("/rtbio/ecg/ibi", ecg_receive)

        server = osc_server.ThreadingOSCUDPServer(
            ('127.0.0.1', 4810), dispatcher)
        print("Serving on {}".format(server.server_address))
        server.serve_forever()
    except IndexError:
        raise ValueError('Give serial port as argument')
