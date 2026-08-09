"""
retrain_real.py

Retrains the LSTM autoencoder on real logged network data
(network_dataset.csv from log_dataset.py), using a chronological
split (no shuffling) so create_windows() produces true time-sequences.

Run from the training/ directory:
    python retrain_real.py
"""

import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint

from preprocessing.clean import clean_dataset
from preprocessing.feature_engineering import engineer_features
from preprocessing.normalize import normalize_dataset, FEATURE_COLUMNS
from preprocessing.create_windows import create_windows

from networks.lstm_autoencoder import build_lstm_autoencoder

from utils.config import DATASET_PATH, WINDOW_SIZE, EPOCHS, BATCH_SIZE, MODEL_DIR

MODEL_PATH = os.path.join(MODEL_DIR, "lstm_autoencoder_real.keras")
THRESHOLD_PATH = os.path.join(MODEL_DIR, "threshold_real.npy")

os.makedirs(MODEL_DIR, exist_ok=True)

# =====================================================
# 1. Load, clean, engineer, normalize
# =====================================================

print("\nSTEP 1 - Cleaning Dataset")
df = clean_dataset(DATASET_PATH)

print("\nSTEP 2 - Feature Engineering")
df = engineer_features(df)

print("\nSTEP 3 - Normalization")
df = normalize_dataset(df)  # also saves models/scaler.pkl with real mean/std

# =====================================================
# 2. Chronological split (NOT random -- preserves time order)
# =====================================================

print("\nSTEP 4 - Chronological Train/Val/Test Split")

n = len(df)
train_end = int(n * 0.70)
val_end = int(n * 0.85)

df_train = df.iloc[:train_end]
df_val = df.iloc[train_end:val_end]
df_test = df.iloc[val_end:]

print(f"Train: {len(df_train)}  Val: {len(df_val)}  Test: {len(df_test)}")

X_train = df_train[FEATURE_COLUMNS].values
X_val = df_val[FEATURE_COLUMNS].values
X_test = df_test[FEATURE_COLUMNS].values

# =====================================================
# 3. Create windows (within each contiguous chunk)
# =====================================================

print("\nSTEP 5 - Creating Windows")

X_train_w = create_windows(X_train, window_size=WINDOW_SIZE)
X_val_w = create_windows(X_val, window_size=WINDOW_SIZE)
X_test_w = create_windows(X_test, window_size=WINDOW_SIZE)

print("Train shape :", X_train_w.shape)
print("Val shape   :", X_val_w.shape)
print("Test shape  :", X_test_w.shape)

# =====================================================
# 4. Build & train model
# =====================================================

print("\nSTEP 6 - Building Model")

model = build_lstm_autoencoder(
    window_size=WINDOW_SIZE,
    n_features=X_train_w.shape[2],
)
model.summary()

print("\nSTEP 7 - Training")

callbacks = [
    EarlyStopping(monitor="val_loss", patience=10, restore_best_weights=True),
    ModelCheckpoint(MODEL_PATH, save_best_only=True, monitor="val_loss"),
]

history = model.fit(
    X_train_w, X_train_w,
    validation_data=(X_val_w, X_val_w),
    epochs=EPOCHS,
    batch_size=BATCH_SIZE,
    callbacks=callbacks,
    verbose=1,
)

model.save(MODEL_PATH)
print(f"\nModel saved to: {MODEL_PATH}")

# =====================================================
# 5. Compute new threshold (same methodology as before)
# =====================================================

print("\nSTEP 8 - Computing Threshold")

train_pred = model.predict(X_train_w, verbose=0)
test_pred = model.predict(X_test_w, verbose=0)

train_mse = np.mean(np.square(X_train_w - train_pred), axis=(1, 2))
test_mse = np.mean(np.square(X_test_w - test_pred), axis=(1, 2))

threshold = np.mean(train_mse) + 3 * np.std(train_mse)

print(f"\nNew threshold: {threshold:.7f}")
print(f"Train MSE  -> mean: {np.mean(train_mse):.6f}  std: {np.std(train_mse):.6f}")
print(f"Test MSE   -> mean: {np.mean(test_mse):.6f}  std: {np.std(test_mse):.6f}")
print(f"Test MSE   -> max:  {np.max(test_mse):.6f}   (should be < threshold for clean data)")

np.save(THRESHOLD_PATH, np.array([threshold]))
print(f"\nThreshold saved to: {THRESHOLD_PATH}")
