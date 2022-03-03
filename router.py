import time
import websockets
from threading import Thread

from pythonosc import osc_message_builder
from pythonosc import udp_client
from wsserver import WSServer


class Router():
    def __init__(self):
        self.osc_client = None
        self.ws_server = None
        self.file_handle = None
        self.osc_prefix = None
        self.osc_address = None
        self.filename = None
        self.ws_port = None
        def digital_out():
            pass
        self.digital_out_func = digital_out

    def init_destinations(self, connections):

        destinations = []
        for connection in connections.values():
            destinations += connection

        if 'osc' in destinations:
            print('connecting osc to ' + self.osc_address)
            address_port = self.osc_address.split(':')
            self.osc_client = udp_client.SimpleUDPClient(address_port[0], int(address_port[1]))
        if 'file' in destinations:
            self.file_handle = open(self.filename, 'w')
            print("initializing file " + self.filename)
        if 'ws' in destinations:
            self.ws_server = WSServer(self.ws_port)


    def route_data(self, source, connections, features, raw_data):
        source_connections = []
        if source in connections:
            source_connections += connections[source]

        current_time = time.time()
        
        # raw data
        if 'r' + source in connections:
            source_connections += connections['r' + source]
            for destination in connections['r' + source]: 
                for i, channel in enumerate(raw_data):
                    if i > 0:
                        source += str(i)

                    osc_dest = '/{}/raw'.format(source)
                    if destination == 'osc':
                        for data in channel:
                            osc_address = self.osc_prefix + osc_dest
                            self.osc_client.send_message(osc_address, data)
                    elif destination == 'file':
                        self.file_handle.write('{} {}: {}\n'.format(current_time, osc_dest, str(raw_data)))
                    elif destination == 'ws':
                        self.ws_server.add_message('{}|{}/{}'.format(current_time, osc_dest, str(raw_data)))


        # features
        if features:
            for destination in source_connections:
                for i, features_chan in enumerate(features):
                    if i > 0:
                        source += str(i)
                    if features_chan:
                        for feature in features_chan.keys():
                            osc_dest = '/{}/{}'.format(source, feature)
                            for data in features_chan[feature]:
                                if destination == 'osc':
                                    self.osc_client.send_message(self.osc_prefix + osc_dest, data)
                                elif destination == 'file':
                                    self.file_handle.write('{} {}: {}\n'.format(current_time, osc_dest, str(data)))
                                elif destination == 'ws':
                                    self.ws_server.add_message('{}|{}/{}'.format(current_time, osc_dest, str(data)))
                                elif destination == 'digital':
                                    if self.digital_out_func:
                                        self.digital_out_func()
                                    


