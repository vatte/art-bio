
import asyncio
import websockets
from threading import Thread


all_websockets = []

class WSServer():
    def __init__(self):
        self.all_websockets = []
        self.run()

    def add_message(self, message):
        for websocket in self.all_websockets:
            websocket.art_bio_messages.append(message)
    
    def run(self):
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
            asyncio.set_event_loop(loop)
            server = websockets.serve(data, '127.0.0.1', 5678)
            loop.run_until_complete(server)
            loop.run_forever()

        loop = asyncio.new_event_loop()
        thread = Thread(target = run_server, args=(loop,))
        thread.start()


if __name__ == "__main__":
    wsserver = WSServer()

    import time

    while True:
        wsserver.add_message('/ecg/raw/[1 2 3 4 5]')
        time.sleep(1)