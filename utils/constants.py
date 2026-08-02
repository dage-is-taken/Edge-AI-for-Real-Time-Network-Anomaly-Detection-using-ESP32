# Dataset

FEATURE_COLUMNS = [
    "latency_ms",
    "jitter_ms",
    "packet_loss_percent",
    "throughput_mbps",
    "rssi_dbm",
]

LABEL_COLUMN = "label"

NORMAL_LABEL = 0
ANOMALY_LABEL = 1

# Windowing

DEFAULT_WINDOW_SIZE = 10

# Random seed

RANDOM_STATE = 42