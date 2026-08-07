
import os
import tensorflow as tf
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint

from preprocessing.clean import clean_dataset
from preprocessing.feature_engineering import engineer_features
from preprocessing.normalize import normalize_dataset
from preprocessing.split_dataset import split_dataset
from preprocessing.create_windows import create_windows

from networks.lstm_autoencoder import build_lstm_autoencoder

from utils.config import (
    DATASET_PATH,
    WINDOW_SIZE,
    EPOCHS,
    BATCH_SIZE,
    PATIENCE,
)

MODEL_DIR = "models"
MODEL_PATH = os.path.join(MODEL_DIR, "lstm_autoencoder.keras")

os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)

# =====================================================
# 1. Load and clean dataset
# =====================================================

print("\nSTEP 1 - Cleaning Dataset")

df = clean_dataset(DATASET_PATH)
# =====================================================
# 2. Feature Engineering
# =====================================================

print("\nSTEP 2 - Feature Engineering")

df = engineer_features(df)

# =====================================================
# 3. Normalize
# =====================================================

print("\nSTEP 3 - Normalization")

df = normalize_dataset(df)

# =====================================================
# 4. Split Dataset
# =====================================================

print("\nSTEP 4 - Train/Test Split")

(
    X_train,
    X_val,
    X_test,
    y_train,
    y_val,
    y_test,
) = split_dataset(df)

# =====================================================
# 5. Train ONLY on normal traffic
# =====================================================

print("\nSTEP 5 - Keeping only NORMAL samples")

X_train = X_train[y_train == 0]

print(f"Training samples (normal only): {len(X_train)}")

# =====================================================
# 6. Create Windows
# =====================================================

print("\nSTEP 6 - Creating Windows")

X_train = create_windows(X_train, window_size=WINDOW_SIZE)

X_val, y_val = create_windows(
    X_val,
    y_val,
    window_size=WINDOW_SIZE
)

X_test, y_test = create_windows(
    X_test,
    y_test,
    window_size=WINDOW_SIZE
)

print("Train shape :", X_train.shape)
print("Val shape   :", X_val.shape)
print("Test shape  :", X_test.shape)

# =====================================================
# 7. Build Model
# =====================================================

print("\nSTEP 7 - Building Model")

model = build_lstm_autoencoder(
    window_size=WINDOW_SIZE,
    n_features=X_train.shape[2]
)

model.summary()

# =====================================================
# 8. Train
# =====================================================

print("\nSTEP 8 - Training")

callbacks = [

    EarlyStopping(
        monitor="val_loss",
        patience=10,
        restore_best_weights=True,
    ),

    ModelCheckpoint(
        MODEL_PATH,
        save_best_only=True,
        monitor="val_loss",
    ),
]

history = model.fit(

    X_train,
    X_train,

    validation_data=(X_val, X_val),

    epochs=EPOCHS,

    batch_size=BATCH_SIZE,

    callbacks=callbacks,

    verbose=1,
)

# =====================================================
# 9. Save Model
# =====================================================

model.save(MODEL_PATH)

print("\nTraining Finished.")

print(f"\nModel saved to:\n{MODEL_PATH}")