#!/bin/sh

cd $(dirname $0)
case "$1" in
    server)
    exec /home/docker/data/bin/hypercorn --quic-bind 0.0.0.0:4433 --certfile /keys/cert.pem --keyfile /keys/key.pem --bind 0.0.0.0:8000 mozhttp3server.run:app --access-logfile -
    ;;

    *)
        echo "Unknown CMD, $1"
        exit 1
        ;;
esac
