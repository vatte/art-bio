
import asyncio
import websockets
from threading import Thread
import ssl
import pathlib

all_websockets = []


class WSServer():
    def __init__(self, port = 5678):
        self.all_websockets = []
        self.loop = None
        #self.ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        #path_cert = pathlib.Path(__file__).with_name("cert.pem")
        #path_key = pathlib.Path(__file__).with_name("key.pem")
        #self.ssl_context.load_cert_chain(path_cert, keyfile=path_key)

        self.run(port)

    def add_message(self, message):
        for websocket in self.all_websockets:
            websocket.art_bio_messages.append(message)
    
    def run(self, port):
        async def data(websocket, path):
            self.all_websockets.append(websocket)
            websocket.art_bio_messages = []
            while True:
                messages = websocket.art_bio_messages
                for message in messages:
                    await websocket.send(message)
                websocket.art_bio_messages = []
                await asyncio.sleep(0.1)

        def run_server(loop):
            print('websocket server starting on port ' + str(port))
            asyncio.set_event_loop(loop)
            #server = websockets.serve(data, '127.0.0.1', port, ssl=self.ssl_context)
            server = websockets.serve(data, '127.0.0.1', port)
            loop.run_until_complete(server)
            loop.run_forever()

        self.loop = asyncio.new_event_loop()
        thread = Thread(target = run_server, args=(self.loop,))
        thread.start()

    def stop(self):
        self.loop.call_soon_threadsafe(self.loop.stop)
        self.loop.call_soon_threadsafe(self.loop.close)
        #self.loop.close()


if __name__ == "__main__":
    wsserver = WSServer()

    import time

    while True:
        wsserver.add_message('/ecg/raw/[1 2 3 4 5]')
        time.sleep(1)
