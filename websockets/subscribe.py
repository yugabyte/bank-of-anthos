#!/usr/bin/env python3
# subscribe to a Redis pubsub channel and output to stdout

import redis
import json
import sys

REDIS_HOST="redis"
REDIS_PORT=6379
CHANNEL="xactions"

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)
pubsub = r.pubsub()
pubsub.subscribe(CHANNEL)
try:
    for message in pubsub.listen():
        # messages have this format:
        # {'type': 'message', 'pattern': None, 'channel': b'chan', 'data': b'hello world'}
        # get messages only, ignore subscription notifications
        if message.get("type") == "message":
            print(message['data'].decode('utf-8'))
            sys.stdout.flush()

except KeyboardInterrupt as err:
    pass
