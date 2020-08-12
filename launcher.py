#!/usr/bin/python
import subprocess
import argparse


server = ["/home/docker/data/bin/hypercorn",
          "--quic-bind", "0.0.0.0:4433",
          "--certfile", "/keys/cert.pem",
          "--keyfile", "/keys/key.pem",
          "--bind", "0.0.0.0:8000",
          "--access-logfile", "-",
          "mozhttp3server.run:app"]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load test.")

    parser.add_argument(
        "action",
        default="server",
        help="what to run",
        nargs="?",
    )

    args = parser.parse_args()

    if args.action != "server":
        raise NotImplementedError(args.action)

    subprocess.run(server, check=True)
