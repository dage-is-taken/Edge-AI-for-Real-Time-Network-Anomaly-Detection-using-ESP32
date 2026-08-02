from preprocessing.clean import clean_dataset
from preprocessing.feature_engineering import engineer_features
from preprocessing.normalize import normalize_dataset
from preprocessing.split_dataset import split_dataset
from preprocessing.create_windows import create_windows

from utils.config import DATASET_PATH, WINDOW_SIZE


def main():

    print("=" * 70)
    print("NETWORK ANOMALY DETECTION PREPROCESSING PIPELINE")
    print("=" * 70)

    # --------------------------------------------------
    # Load dataset
    # --------------------------------------------------

    df = clean_dataset(DATASET_PATH)

    print(f"\nDataset shape: {df.shape}")

    # --------------------------------------------------
    # Feature engineering
    # --------------------------------------------------

    df = engineer_features(df)

    print(f"\nAfter feature engineering: {df.shape}")

    # --------------------------------------------------
    # Normalize
    # --------------------------------------------------

    df = normalize_dataset(df)

    # --------------------------------------------------
    # Split
    # --------------------------------------------------

    (
        X_train,
        X_val,
        X_test,
        y_train,
        y_val,
        y_test,
    ) = split_dataset(df)

    # --------------------------------------------------
    # Windows
    # --------------------------------------------------

    X_train = create_windows(
        X_train,
        window_size=WINDOW_SIZE,
    )

    X_val, y_val = create_windows(
        X_val,
        y_val,
        window_size=WINDOW_SIZE,
    )

    X_test, y_test = create_windows(
        X_test,
        y_test,
        window_size=WINDOW_SIZE,
    )

    print("\n")
    print("=" * 70)
    print("FINAL SHAPES")
    print("=" * 70)

    print("Train :", X_train.shape)
    print("Validation :", X_val.shape)
    print("Test :", X_test.shape)

    print("\nPipeline completed successfully!")


if __name__ == "__main__":
    main()