#!/usr/bin/python
import subprocess
import argparse
import shlex


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="http3 launcher")

    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="host"
    )

    parser.add_argument(
        "--cert",
        type=str,
        default="keys/cert.pem",
        help="certificate"
    )

    parser.add_argument(
        "--key",
        type=str,
        default="keys/key.pem",
        help="key"
    )

    parser.add_argument(
        "--h2-port",
        type=int,
        default=443,
        help="HTTP/2 port"
    )

    parser.add_argument(
        "--h3-port",
        type=int,
        default=4433,
        help="HTTP/3 port"
    )

    args = parser.parse_args()

    cmd = ("bin/hypercorn "
              f"--quic-bind {args.host}:{args.h3_port} "
              f"--certfile {args.cert} "
              f"--keyfile {args.key} "
              f"--bind {args.host}:{args.h2_port} "
              "--access-logfile - "
              "mozhttp3server.run:app")

    subprocess.run(shlex.split(cmd), check=True)
