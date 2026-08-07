import tensorflow as tf
from tensorflow.keras import Model
from tensorflow.keras.layers import (
    Input,
    Flatten,
    Dense,
    Reshape,
)


def build_lstm_autoencoder(
    window_size=10,
    n_features=8,
):

    inputs = Input(shape=(window_size, n_features))

    x = Flatten()(inputs)

    x = Dense(64, activation="relu")(x)

    x = Dense(32, activation="relu")(x)

    bottleneck = Dense(16, activation="relu")(x)

    x = Dense(32, activation="relu")(bottleneck)

    x = Dense(64, activation="relu")(x)

    x = Dense(window_size * n_features)(x)

    outputs = Reshape(
        (window_size, n_features)
    )(x)

    model = Model(inputs, outputs)

    model.compile(
        optimizer="adam",
        loss="mse",
    )

    return model


if __name__ == "__main__":

    model = build_lstm_autoencoder()

    model.summary()