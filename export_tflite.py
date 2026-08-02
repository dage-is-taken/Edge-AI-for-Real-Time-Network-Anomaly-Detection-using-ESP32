import tensorflow as tf
import os

KERAS_MODEL = "models/lstm_autoencoder.keras"
TFLITE_MODEL = "models/model.tflite"

print("Loading model...")

model = tf.keras.models.load_model(KERAS_MODEL)

converter = tf.lite.TFLiteConverter.from_keras_model(model)

converter.optimizations = [tf.lite.Optimize.DEFAULT]

# Required for LSTM models
converter.target_spec.supported_ops = [
    tf.lite.OpsSet.TFLITE_BUILTINS,
    tf.lite.OpsSet.SELECT_TF_OPS,
]

converter._experimental_lower_tensor_list_ops = False

print("Converting...")

tflite_model = converter.convert()

os.makedirs("models", exist_ok=True)

with open(TFLITE_MODEL, "wb") as f:
    f.write(tflite_model)

print("Done!")
print("Saved:", TFLITE_MODEL)