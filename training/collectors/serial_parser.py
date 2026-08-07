from training.utils.constants import SERIAL_PREFIX


def parse_line(line: str):
    """
    Parse a DATA line coming from the ESP32.

    Expected format:

    DATA,timestamp,latency,jitter,loss,throughput,rssi
    """

    line = line.strip()

    if not line.startswith(SERIAL_PREFIX):
        return None

    parts = line.split(",")

    if len(parts) != 7:
        return None

    try:

        return {
            "timestamp_ms": int(parts[1]),
            "latency_ms": float(parts[2]),
            "jitter_ms": float(parts[3]),
            "packet_loss_pct": float(parts[4]),
            "throughput_mbps": float(parts[5]),
            "rssi_dbm": int(parts[6]),
        }

    except ValueError:

        return None