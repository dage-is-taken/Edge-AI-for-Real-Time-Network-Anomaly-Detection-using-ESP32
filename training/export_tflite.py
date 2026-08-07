import tensorflow as tf

model = tf.keras.models.load_model("models/lstm_autoencoder.keras")

converter = tf.lite.TFLiteConverter.from_keras_model(model)

# REMOVE ALL THESE LINES:
# converter.optimizations = [tf.lite.Optimize.DEFAULT]
# converter.target_spec.supported_ops = [...]
# converter._experimental_lower_tensor_list_ops = False

tflite_model = converter.convert()

with open("models/model.tflite", "wb") as f:
    f.write(tflite_model)

print("Done")