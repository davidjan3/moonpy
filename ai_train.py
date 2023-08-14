# import os
# os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
# os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

import pandas as pd
import tensorflow as tf

from ai_util import makeSets, toDataset

model = tf.keras.models.Sequential(
    [
        tf.keras.layers.Input(shape=(1, 2 * 16)),
        tf.keras.layers.Dense(128, activation=tf.keras.activations.tanh),
        tf.keras.layers.Dense(64, activation=tf.keras.activations.tanh),
        tf.keras.layers.Dense(32, activation=tf.keras.activations.tanh),
        tf.keras.layers.Dense(16, activation=tf.keras.activations.tanh),
        tf.keras.layers.Dense(4, activation=tf.keras.activations.tanh),
        tf.keras.layers.Dense(1, activation=tf.keras.activations.tanh),
    ]
)

model.compile(
    optimizer=tf.keras.optimizers.SGD(learning_rate=0.001, momentum=0.6),
    loss=tf.keras.losses.MeanSquaredError(),
)

print("Loading CSV...")
btc = pd.read_csv("./data/mBTC_idx.csv")
btc["Time"] = pd.to_datetime(btc["Time"], unit="s")
btc = btc.set_index("Time")
btcTrain = btc.loc["2019-01-01":"2021-12-31"]
x_train, y_train = makeSets(btcTrain)

# Create train dataset and call model.fit with it:
print("Creating datasets...")
train_dataset = toDataset(x_train, y_train)

print("Training...")
model.fit(
    train_dataset,
    epochs=50,
    callbacks=[
        tf.keras.callbacks.EarlyStopping(
            monitor="loss", min_delta=0.00005, patience=3, restore_best_weights=True
        )
    ],
)
model.save("models/model2.keras")
