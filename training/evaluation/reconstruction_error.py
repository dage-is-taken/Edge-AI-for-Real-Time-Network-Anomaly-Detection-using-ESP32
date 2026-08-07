import numpy as np
import tensorflow as tf
import joblib

from preprocessing.clean import clean_dataset
from preprocessing.feature_engineering import engineer_features
from preprocessing.normalize import normalize_dataset
from preprocessing.split_dataset import split_dataset
from preprocessing.create_windows import create_windows

from utils.config import DATASET_PATH, WINDOW_SIZE

# Load model
model = tf.keras.models.load_model("models/lstm_autoencoder.keras")

# Load data
df = clean_dataset(DATASET_PATH)
df = engineer_features(df)
df = normalize_dataset(df)

X_train, X_val, X_test, y_train, y_val, y_test = split_dataset(df)

# Only normal samples for threshold
X_train = X_train[y_train == 0]

X_train = create_windows(X_train, window_size=WINDOW_SIZE)
X_test, y_test = create_windows(X_test, y_test, window_size=WINDOW_SIZE)

print("Predicting train...")
train_pred = model.predict(X_train, verbose=0)

print("Predicting test...")
test_pred = model.predict(X_test, verbose=0)

train_mse = np.mean(np.square(X_train - train_pred), axis=(1,2))
test_mse  = np.mean(np.square(X_test - test_pred), axis=(1,2))

threshold = np.mean(train_mse) + 3*np.std(train_mse)

print()
print("Threshold:", threshold)

predictions = (test_mse > threshold).astype(int)

accuracy = np.mean(predictions == y_test)

print("Accuracy:", accuracy)

np.save("models/threshold.npy", np.array([threshold]))