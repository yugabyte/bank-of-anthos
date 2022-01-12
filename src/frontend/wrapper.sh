#!/bin/bash
# wrapper script to start multiple services in a single container.
#
# $PORT is for gunicorn
# $WEBSOCKET_PORT is for websocketd

# start gunicorn as a daemon
gunicorn --daemon -b :$PORT --threads 4 --log-config /logging.conf --log-level=$LOG_LEVEL "frontend:create_app()"

# start websocketd
/usr/bin/websocketd --port=$WEBSOCKET_PORT /subscribe.py
