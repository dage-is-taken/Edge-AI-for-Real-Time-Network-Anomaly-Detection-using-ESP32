#!/usr/bin/env python3
"""
log_dataset.py

Listens on the ESP32's serial port, parses lines of the form:
    DATA,timestamp,latency,jitter,loss,throughput,rssi

and appends them to a CSV file for later retraining.

Usage:
    python log_dataset.py --port /dev/ttyUSB0
    python log_dataset.py --port COM5          (Windows)

Press Ctrl+C to stop. Safe to stop/restart -- it appends, never overwrites,
and writes each row immediately so you don't lose data on a crash/unplug.
"""

import argparse
import csv
import os
import sys
import time
from datetime import datetime

try:
    import serial
except ImportError:
    print("Missing dependency. Install it with:")
    print("    pip install pyserial --break-system-packages")
    sys.exit(1)


CSV_HEADER = [
    "logged_at",       # wall-clock time we received the line (ISO format)
    "esp_millis",      # ESP32's own millis() timestamp
    "latency_ms",
    "jitter_ms",
    "loss_percent",
    "throughput_mbps",
    "rssi_dbm",
]


def parse_data_line(line: str):
    """
    Expects: DATA,196461,2.85,1.26,0.00,2.99,-30
    Returns a dict of parsed values, or None if the line doesn't match.
    """
    parts = line.strip().split(",")

    if len(parts) != 7 or parts[0] != "DATA":
        return None

    try:
        return {
            "esp_millis": int(parts[1]),
            "latency_ms": float(parts[2]),
            "jitter_ms": float(parts[3]),
            "loss_percent": float(parts[4]),
            "throughput_mbps": float(parts[5]),
            "rssi_dbm": int(parts[6]),
        }
    except ValueError:
        # malformed number in the line -- skip it rather than crash
        return None


def main():
    parser = argparse.ArgumentParser(description="Log ESP32 anomaly detector data to CSV")
    parser.add_argument("--port", required=True, help="Serial port, e.g. /dev/ttyUSB0 or COM5")
    parser.add_argument("--baud", type=int, default=115200, help="Baud rate (default 115200)")
    parser.add_argument("--out", default="network_dataset.csv", help="Output CSV file path")
    args = parser.parse_args()

    file_exists = os.path.isfile(args.out)

    print(f"Opening {args.port} @ {args.baud} baud...")
    try:
        ser = serial.Serial(args.port, args.baud, timeout=1)
    except serial.SerialException as e:
        print(f"ERROR: could not open serial port: {e}")
        print("Tips:")
        print("  - Check the port name (ls /dev/ttyUSB* on Linux/WSL, Device Manager on Windows)")
        print("  - Make sure no other program (Arduino IDE, PlatformIO monitor) has it open")
        print("  - On WSL2, USB passthrough must be attached (usbipd) for /dev/ttyUSB0 to exist")
        sys.exit(1)

    # give the ESP32 a moment (some boards reset on serial open)
    time.sleep(2)

    row_count = 0
    skipped_count = 0

    with open(args.out, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADER)

        if not file_exists:
            writer.writeheader()

        print(f"Logging to {args.out}  (Ctrl+C to stop)")
        print("-" * 50)

        try:
            while True:
                try:
                    raw = ser.readline()
                except serial.SerialException:
                    print("Serial connection lost. Is the board still plugged in?")
                    break

                if not raw:
                    continue

                try:
                    line = raw.decode("utf-8", errors="ignore").strip()
                except UnicodeDecodeError:
                    continue

                if not line:
                    continue

                if line.startswith("DATA,"):
                    parsed = parse_data_line(line)

                    if parsed is None:
                        skipped_count += 1
                        print(f"  [skip] malformed line: {line}")
                        continue

                    row = {"logged_at": datetime.now().isoformat(timespec="seconds")}
                    row.update(parsed)

                    writer.writerow(row)
                    f.flush()  # write immediately so we don't lose data on crash/unplug

                    row_count += 1
                    print(
                        f"[{row_count:4d}] latency={parsed['latency_ms']:.2f}ms  "
                        f"jitter={parsed['jitter_ms']:.2f}ms  "
                        f"loss={parsed['loss_percent']:.1f}%  "
                        f"throughput={parsed['throughput_mbps']:.2f}Mbps  "
                        f"rssi={parsed['rssi_dbm']}dBm"
                    )
                else:
                    # Not a DATA line -- just the normal human-readable serial output.
                    # Print it through so you still see live status, but don't log it.
                    print(f"  {line}")

        except KeyboardInterrupt:
            print()
            print("-" * 50)
            print(f"Stopped. Logged {row_count} rows ({skipped_count} skipped) to {args.out}")

    ser.close()


if __name__ == "__main__":
    main()
