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
            self.ws_server = WSServer()


    def route_data(self, source, connections, features, raw_data):
        source_connections = []
        if source in connections:
            source_connections += connections[source]

        current_time = time.time()
        
        # raw data
        if 'r' + source in connections:
            source_connections += connections['r' + source]
            for destination in connections['r' + source]: 
                osc_dest = '/{}/raw'.format(source)
                if destination == 'osc':
                    for data in raw_data:
                        self.osc_client.send_message(self.osc_prefix + osc_dest, data)
                elif destination == 'file':
                    self.file_handle.write('{} {}: {}\n'.format(current_time, osc_dest, str(raw_data)))
                elif destination == 'ws':
                    self.ws_server.add_message('{}|{}/{}'.format(current_time, osc_dest, str(raw_data)))


        # features
        if features:
            for destination in source_connections:
                for feature in features.keys():
                    osc_dest = '/{}/{}'.format(source, feature)
                    #for data in features[feature]:
                    data = features[feature]
                    if destination == 'osc':
                        self.osc_client.send_message(self.osc_prefix + osc_dest, data)
                    elif destination == 'file':
                        self.file_handle.write('{} {}: {}\n'.format(current_time, osc_dest, str(data)))
                    elif destination == 'ws':
                        self.ws_server.add_message('{}|{}/{}'.format(current_time, osc_dest, str(raw_data)))
                    elif destination == 'digital':
                        if self.digital_out_func:
                            self.digital_out_func()


