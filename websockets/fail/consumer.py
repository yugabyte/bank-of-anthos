# consumer.py

import asyncio
from aioredis import create_connection, Channel
import websockets

async def publish_to_redis(msg, path):
    # Connect to Redis
    conn = await create_connection(('localhost', 6379))

    # Publish to channel "lightlevel{path}"
    await conn.execute('publish', 'lightlevel{}'.format(path), msg)


async def server(websocket, path):
    try:
        while True:
            # Receive data from "the outside world"
            message = await websocket.recv()

            # Feed this data to the PUBLISH co-routine
            await publish_to_redis(message, path) 

            await asyncio.sleep(1)

    except websockets.exceptions.ConnectionClosed:
        print('Connection Closed!')

if __name__ == '__main__':
    # Boiler-plate for the websocket server, running on localhost, port 8765
    loop = asyncio.get_event_loop()
    loop.set_debug(True)
    ws_server = websockets.serve(server, 'localhost', 8765)
    loop.run_until_complete(ws_server)
    loop.run_forever()
