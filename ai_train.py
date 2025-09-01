# import os
# os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
# os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

import pandas as pd
import tensorflow as tf
import ai_util as ut

INPUT_LEN = 32

model = tf.keras.models.Sequential(
    [
        tf.keras.layers.Input(shape=(INPUT_LEN, 16)),
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(512, activation=tf.keras.activations.tanh),
        tf.keras.layers.Dense(1024, activation=tf.keras.activations.tanh),
        tf.keras.layers.Dense(256, activation=tf.keras.activations.tanh),
        tf.keras.layers.Dense(32, activation=tf.keras.activations.tanh),
        tf.keras.layers.Dense(1, activation=tf.keras.activations.tanh),
    ]
)

model.compile(
    optimizer=tf.keras.optimizers.Adam(),
    loss=tf.keras.losses.MeanSquaredError(),
)

print("Loading CSV...")
btc = pd.read_csv("./data/mBTC_idx.csv")
btc["Time"] = pd.to_datetime(btc["Time"], unit="s")
btc = btc.set_index("Time")
btcTrain = btc.loc["2020-01-01":"2021-12-31"]
btcTrain = btcTrain.dropna()
x_train, y_train = ut.makeSets(btcTrain, INPUT_LEN)

print("Creating datasets...")
train_dataset = ut.toDataset(x_train, y_train).batch(256)

print("Training...")
model.fit(
    train_dataset,
    epochs=200,
    callbacks=[
        tf.keras.callbacks.EarlyStopping(
            monitor="loss", min_delta=0.00005, patience=5, restore_best_weights=True
        )
    ],
)
model.save("models/model11.keras")
