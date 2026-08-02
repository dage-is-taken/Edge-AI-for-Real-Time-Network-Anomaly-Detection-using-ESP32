from pathlib import Path

# ==========================================
# Paths
# ==========================================

ROOT_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = ROOT_DIR / "data"

MODEL_DIR = ROOT_DIR / "models"

DATASET_PATH = DATA_DIR / "network_dataset.csv"

SCALER_PATH = MODEL_DIR / "scaler.pkl"

MODEL_PATH = MODEL_DIR / "lstm_autoencoder.keras"

# ==========================================
# Training
# ==========================================

WINDOW_SIZE = 10

EPOCHS = 50

BATCH_SIZE = 32

LEARNING_RATE = 1e-3

TRAIN_RATIO = 0.70

VALIDATION_RATIO = 0.15

TEST_RATIO = 0.15

# ==========================================
# Early stopping
# ==========================================

PATIENCE = 10

# ==========================================
# TensorFlow Lite
# ==========================================

TFLITE_MODEL = MODEL_DIR / "network_autoencoder.tflite"