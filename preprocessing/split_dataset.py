import pandas as pd
from sklearn.model_selection import train_test_split

FEATURE_COLUMNS = [
    "latency_ms",
    "jitter_ms",
    "packet_loss_percent",
    "throughput_mbps",
    "rssi_dbm",
    "signal_quality",
    "network_stability",
    "packet_efficiency",
]


def split_dataset(df: pd.DataFrame):
    """
    Split the normalized dataset into
    Train / Validation / Test.
    """

    print("=" * 60)
    print("Splitting Dataset")
    print("=" * 60)

    X = df[FEATURE_COLUMNS]

    y = df["label"]

    # -----------------------------
    # Train / Temp
    # -----------------------------

    X_train, X_temp, y_train, y_temp = train_test_split(
        X,
        y,
        test_size=0.30,
        random_state=42,
        stratify=y,
    )

    # -----------------------------
    # Validation / Test
    # -----------------------------

    X_val, X_test, y_val, y_test = train_test_split(
        X_temp,
        y_temp,
        test_size=0.50,
        random_state=42,
        stratify=y_temp,
    )

    print()

    print(f"Training samples   : {len(X_train)}")
    print(f"Validation samples : {len(X_val)}")
    print(f"Testing samples    : {len(X_test)}")

    return (
        X_train,
        X_val,
        X_test,
        y_train,
        y_val,
        y_test,
    )