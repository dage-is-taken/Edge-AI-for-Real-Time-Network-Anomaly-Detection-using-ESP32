import argparse
import threading
import time
import requests

parser = argparse.ArgumentParser(description="HTTP Load Generator")

parser.add_argument(
    "--host",
    default="192.168.1.126",
    help="HTTP server IP"
)

parser.add_argument(
    "--port",
    default=8000,
    type=int,
    help="HTTP server port"
)

parser.add_argument(
    "--threads",
    default=20,
    type=int,
    help="Number of concurrent workers"
)

parser.add_argument(
    "--path",
    default="/testfile.bin",
    help="File to download"
)

args = parser.parse_args()

URL = f"http://{args.host}:{args.port}{args.path}"

print("=" * 60)
print("HTTP LOAD GENERATOR")
print("=" * 60)
print(f"Target  : {URL}")
print(f"Threads : {args.threads}")
print("=" * 60)

total_requests = 0
lock = threading.Lock()


def worker(worker_id):

    global total_requests

    session = requests.Session()

    while True:

        try:

            r = session.get(URL, timeout=10)

            # Read the body so the download actually happens
            _ = r.content

            with lock:
                total_requests += 1

                if total_requests % 25 == 0:
                    print(
                        f"[{total_requests}] "
                        f"Status={r.status_code} "
                        f"Worker={worker_id}"
                    )

        except Exception:
            pass


for i in range(args.threads):

    t = threading.Thread(
        target=worker,
        args=(i,),
        daemon=True
    )

    t.start()

try:

    while True:
        time.sleep(1)

except KeyboardInterrupt:

    print("\nStopping load generator...")