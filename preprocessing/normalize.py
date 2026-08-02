import os
import joblib
import pandas as pd
from sklearn.preprocessing import StandardScaler

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


def normalize_dataset(
    df: pd.DataFrame,
    scaler_path="models/scaler.pkl",
):
    print("=" * 60)
    print("Normalizing Dataset")
    print("=" * 60)

    scaler = StandardScaler()

    normalized = df.copy()

    normalized[FEATURE_COLUMNS] = scaler.fit_transform(
        df[FEATURE_COLUMNS]
    )

    os.makedirs(os.path.dirname(scaler_path), exist_ok=True)

    joblib.dump(scaler, scaler_path)

    print("\nScaler saved.")

    print("\nMeans")

    for feature, mean in zip(FEATURE_COLUMNS, scaler.mean_):
        print(f"{feature:25s}: {mean:.6f}")

    print("\nStandard Deviations")

    for feature, std in zip(FEATURE_COLUMNS, scaler.scale_):
        print(f"{feature:25s}: {std:.6f}")

    return normalized


def load_scaler(path="models/scaler.pkl"):
    return joblib.load(path)