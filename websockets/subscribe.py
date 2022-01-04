#!/usr/bin/env python3
# subscribe to a Redis pubsub channel and output to stdout

import redis
import json
import sys

CHANNEL="chan"

r = redis.Redis(host='localhost', port=6379)
pubsub = r.pubsub()
pubsub.subscribe(CHANNEL)
try:
    for message in pubsub.listen():
        # messages have this format:
        # {'type': 'message', 'pattern': None, 'channel': b'chan', 'data': b'hello world'}
        # get messages only, ignore subscription notifications
        if message.get("type") == "message":
            #print(message)
            print(message['data'].decode('utf-8'))
            sys.stdout.flush()

except KeyboardInterrupt as err:
    pass
