#!/usr/bin/env python3

import asyncio
import websockets
import json

class CyberBot:
    '''
    '''
    def __init__(self):
        self.WS_URI = "ws://map.norsecorp.com/socketcluster/"
        self.events = {
            "#publish": self.handle_publish_event
        }

    async def run(self):
        async with websockets.connect(self.WS_URI) as ws:
            # Send Init messages
            await ws.send("{\"event\":\"#handshake\",\"data\":{\"authToken\":null},\"cid\":1}")
            # TODO: subscribe for all channels (global, europe, us&china...)
            await ws.send("{\"event\":\"#subscribe\",\"data\":{\"channel\":\"global\"},\"cid\":2}")

            # Main thread cycle
            while True:
                try:
                    msg = await asyncio.wait_for(ws.recv(), timeout=10)
                except asyncio.TimeoutError:
                    # No data in 1 second, check the connection.
                    try:
                        pong_waiter = await ws.ping()
                        await asyncio.wait_for(pong_waiter, timeout=20)
                    except asyncio.TimeoutError:
                        # No response to ping, disconnect.
                        print("NO CONNECTION CLOSE")
                        break
                else:
                    if (msg == "#1"): await ws.send("#2")
                    else:
                        try:
                            data = json.loads(msg)
                        except json.JSONDecodeError as e:
                            print(e.msg)
                        else:
                            self.handle_data(data)

    def handle_data(self, data):
        try:
            self.events.get(data['event'], lambda d: print("UNHANDLED EVENT: " + data['event']))(data['data'])
        except KeyError as e:
            print(data)

    def handle_publish_event(self, d):
        # TODO: do some aggregation statistics with the data
        print(d['data'])

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(CyberBot().run())
