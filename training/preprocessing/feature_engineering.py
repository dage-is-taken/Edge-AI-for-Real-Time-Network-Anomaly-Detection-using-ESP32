import pandas as pd


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Perform feature engineering on the cleaned dataset.

    Parameters
    ----------
    df : pandas.DataFrame

    Returns
    -------
    pandas.DataFrame
    """

    print("=" * 60)
    print("Feature Engineering")
    print("=" * 60)

    engineered = df.copy()

    # ----------------------------------------------------
    # Signal Quality
    #
    # Convert RSSI from negative values to a positive
    # signal-strength indicator.
    # Strong Wi-Fi -> larger value
    # ----------------------------------------------------

    engineered["signal_quality"] = engineered["rssi_dbm"] + 100

    # ----------------------------------------------------
    # Network Stability
    #
    # Large jitter relative to latency generally indicates
    # an unstable connection.
    # ----------------------------------------------------

    engineered["network_stability"] = (
        engineered["jitter_ms"] /
        (engineered["latency_ms"] + 1e-6)
    )

    # ----------------------------------------------------
    # Packet Efficiency
    #
    # Higher throughput with lower packet loss is better.
    # ----------------------------------------------------

    engineered["packet_efficiency"] = (
        engineered["throughput_mbps"] *
        (1 - engineered["packet_loss_percent"] / 100.0)
    )

    print("\nCreated features:")

    print("  ✓ signal_quality")
    print("  ✓ network_stability")
    print("  ✓ packet_efficiency")

    print(f"\nTotal features: {len(engineered.columns)-1}")

    return engineered