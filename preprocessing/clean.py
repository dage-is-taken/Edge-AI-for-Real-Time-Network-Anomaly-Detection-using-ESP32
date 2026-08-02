import pandas as pd

FEATURE_COLUMNS = [
    "latency_ms",
    "jitter_ms",
    "packet_loss_percent",
    "throughput_mbps",
    "rssi_dbm",
]

LABEL_COLUMN = "label"


def clean_dataset(csv_path):
    """
    Load and clean the dataset.

    Parameters
    ----------
    csv_path : str
        Path to network_dataset.csv

    Returns
    -------
    pandas.DataFrame
    """

    print("=" * 60)
    print("Loading dataset")
    print("=" * 60)

    df = pd.read_csv(csv_path)

    print(f"Loaded {len(df)} samples")

    # ------------------------------------------------
    # Remove missing values
    # ------------------------------------------------

    before = len(df)
    df = df.dropna()

    print(f"Removed {before-len(df)} rows with missing values")

    # ------------------------------------------------
    # Remove duplicates
    # ------------------------------------------------

    before = len(df)
    df = df.drop_duplicates()

    print(f"Removed {before-len(df)} duplicate rows")

    # ------------------------------------------------
    # Keep only known labels
    # ------------------------------------------------

    df = df[df[LABEL_COLUMN].isin(["normal", "anomaly"])]

    # ------------------------------------------------
    # Convert features to numeric
    # ------------------------------------------------

    for feature in FEATURE_COLUMNS:
        df[feature] = pd.to_numeric(df[feature], errors="coerce")

    df = df.dropna()

    # ------------------------------------------------
    # Remove impossible values
    # ------------------------------------------------

    df = df[df["latency_ms"] >= 0]
    df = df[df["jitter_ms"] >= 0]
    df = df[df["packet_loss_percent"] >= 0]
    df = df[df["packet_loss_percent"] <= 100]

    # Throughput cannot be negative
    df = df[df["throughput_mbps"] >= 0]

    # RSSI should roughly be between -100 and 0 dBm
    df = df[(df["rssi_dbm"] >= -100) & (df["rssi_dbm"] <= 0)]

    # ------------------------------------------------
    # Encode labels
    # ------------------------------------------------

    label_map = {
        "normal": 0,
        "anomaly": 1
    }

    df[LABEL_COLUMN] = df[LABEL_COLUMN].map(label_map)

    print(f"\nFinal dataset size: {len(df)} samples")

    print("\nLabel distribution:")

    print(df[LABEL_COLUMN].value_counts())

    return df