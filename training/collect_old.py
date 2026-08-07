import serial
from serial import SerialException
import csv
import os
import time
from datetime import datetime

# ==============================
# Configuration
# ==============================

SERIAL_PORT = "/dev/serial/by-id/usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0001-if00-port0"
BAUD_RATE = 115200

OUTPUT_DIR = "data"
CSV_FILE = os.path.join(OUTPUT_DIR, "network_dataset.csv")

LABEL = "normal"

# ==============================

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
            "label"
        ])


def connect_serial():
    """Connect to ESP32 and wait until it is ready."""
    while True:
        try:
            print(f"Connecting to {SERIAL_PORT}...")

            ser = serial.Serial(
                SERIAL_PORT,
                BAUD_RATE,
                timeout=1,
                dsrdtr=False,
                rtscts=False
            )

            # Prevent reset if supported
            try:
                ser.dtr = False
                ser.rts = False
            except Exception:
                pass

            # Give ESP32 time to boot
            time.sleep(2)

            # Clear boot messages
            ser.reset_input_buffer()

            print("Connected!\n")

            return ser

        except Exception as e:
            print(f"Connection failed: {e}")
            print("Retrying in 2 seconds...\n")
            time.sleep(2)


print("=" * 50)
print("ESP32 Network Data Collector")
print("=" * 50)
print(f"Serial Port : {SERIAL_PORT}")
print(f"CSV File    : {CSV_FILE}")
print()

ser = connect_serial()

sample = 0

while True:
    try:
        line = ser.readline().decode("utf-8", errors="ignore").strip()

        if not line:
            continue

        if not line.startswith("DATA,"):
            continue

        parts = line.split(",")

        if len(parts) != 7:
            continue

        sample += 1

        timestamp = parts[1]
        latency = float(parts[2])
        jitter = float(parts[3])
        loss = float(parts[4])
        throughput = float(parts[5])
        rssi = int(parts[6])

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open(CSV_FILE, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                now,
                timestamp,
                latency,
                jitter,
                loss,
                throughput,
                rssi,
                LABEL
            ])

        print(
            f"[{sample:05d}] "
            f"Latency={latency:.2f} ms | "
            f"Jitter={jitter:.2f} ms | "
            f"Loss={loss:.2f}% | "
            f"Throughput={throughput:.2f} Mbps | "
            f"RSSI={rssi} dBm"
        )

    except KeyboardInterrupt:
        print("\nStopping collection...")
        break

    except SerialException as e:
        print(f"\nSerial connection lost: {e}")
        print("Reconnecting...\n")

        try:
            ser.close()
        except Exception:
            pass

        ser = connect_serial()

    except Exception as e:
        print(f"\nUnexpected error: {e}")
        time.sleep(1)

try:
    ser.close()
except Exception:
    pass

print("Serial port closed.")