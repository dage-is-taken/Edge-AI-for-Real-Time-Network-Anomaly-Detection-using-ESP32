import argparse
import csv
import os
import time
from datetime import datetime

import serial
from serial import SerialException

# ==================================================
# Arguments
# ==================================================

parser = argparse.ArgumentParser(
    description="ESP32 Network Dataset Collector"
)

parser.add_argument(
    "--label",
    required=True,
    choices=["normal", "anomaly"],
    help="Label assigned to collected samples."
)

parser.add_argument(
    "--samples",
    type=int,
    default=100,
    help="Number of samples to collect."
)

args = parser.parse_args()

# ==================================================
# Configuration
# ==================================================

SERIAL_PORT = "/dev/serial/by-id/usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0001-if00-port0"
BAUD_RATE = 115200

OUTPUT_DIR = "data"
CSV_FILE = os.path.join(OUTPUT_DIR, "network_dataset.csv")

LABEL = args.label
MAX_SAMPLES = args.samples

# ==================================================

os.makedirs(OUTPUT_DIR, exist_ok=True)

if not os.path.exists(CSV_FILE):

    with open(CSV_FILE, "w", newline="") as f:

        writer = csv.writer(f)

        writer.writerow([
            "pc_time",
            "esp_time_ms",
            "latency_ms",
            "jitter_ms",
            "packet_loss_percent",
            "throughput_mbps",
            "rssi_dbm",
            "label",
        ])


def connect():

    while True:

        try:

            print(f"Connecting to {SERIAL_PORT}")

            ser = serial.Serial(
                SERIAL_PORT,
                BAUD_RATE,
                timeout=1,
            )

            time.sleep(2)

            ser.reset_input_buffer()

            print("Connected.\n")

            return ser

        except Exception as e:

            print(e)

            print("Retrying in 2 seconds...\n")

            time.sleep(2)


ser = connect()

sample = 0

print("=" * 60)
print(f"Collecting {MAX_SAMPLES} samples")
print(f"Label : {LABEL}")
print("=" * 60)

while sample < MAX_SAMPLES:

    try:

        line = ser.readline().decode(
            "utf-8",
            errors="ignore"
        ).strip()

        if not line.startswith("DATA,"):
            continue

        parts = line.split(",")

        if len(parts) != 7:
            continue

        sample += 1

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        row = [
            now,
            parts[1],
            float(parts[2]),
            float(parts[3]),
            float(parts[4]),
            float(parts[5]),
            int(parts[6]),
            LABEL,
        ]

        with open(CSV_FILE, "a", newline="") as f:

            csv.writer(f).writerow(row)

        print(
            f"[{sample}/{MAX_SAMPLES}] "
            f"Latency={parts[2]} ms | "
            f"Jitter={parts[3]} ms | "
            f"Loss={parts[4]} % | "
            f"Throughput={parts[5]} Mbps | "
            f"RSSI={parts[6]} dBm"
        )

    except SerialException:

        print("\nSerial disconnected... reconnecting.\n")

        try:
            ser.close()
        except Exception:
            pass

        ser = connect()

print("\nCollection complete!")

ser.close()