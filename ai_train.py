# import os
# os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
# os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

import pandas as pd
import tensorflow as tf

from ai_util import makeSets, toDataset

model = tf.keras.models.Sequential(
    [
        tf.keras.layers.Input(shape=(1, 2 * 16)),
        tf.keras.layers.Dense(64, activation=tf.keras.activations.tanh),
        tf.keras.layers.Dense(32, activation=tf.keras.activations.tanh),
        tf.keras.layers.Dense(16, activation=tf.keras.activations.tanh),
        tf.keras.layers.Dense(8, activation=tf.keras.activations.tanh),
        tf.keras.layers.Dense(4, activation=tf.keras.activations.tanh),
        tf.keras.layers.Dense(2, activation=tf.keras.activations.tanh),
        tf.keras.layers.Dense(1, activation=tf.keras.activations.tanh),
    ]
)

model.compile(
    optimizer=tf.keras.optimizers.RMSprop(0.000025),
    loss=tf.keras.losses.MeanSquaredError(),
)

print("Loading CSV...")
btc = pd.read_csv("./data/mBTC_idx.csv")
btc["Time"] = pd.to_datetime(btc["Time"], unit="s")
btc = btc.set_index("Time")
btcTrain = btc.loc["2021-05-01":"2021-07-31"]
btcTest = btc.loc["2022-09-01":"2022-11-30"]
x_train, y_train = makeSets(btcTrain)
x_test, y_test = makeSets(btcTest)

# Create train dataset and call model.fit with it:
print("Creating datasets...")
train_dataset = toDataset(x_train, y_train)
test_dataset = toDataset(x_test, y_test)

print("Pretesting on trainset:")
model.evaluate(train_dataset, verbose=2)

print("Pretesting on testset:")
model.evaluate(test_dataset, verbose=2)

print("Training...")
model.fit(train_dataset, epochs=20)
model.save("models/model0.keras")

print("Testing on trainset:")
model.evaluate(train_dataset, verbose=2)

print("Testing on testset:")
model.evaluate(test_dataset, verbose=2)

# Remove columns after col 3 from btcTest:
btcTest = btcTest.iloc[:, :5]

# Append model results for test_dataset to btcTest:
predictions = [0] + model.predict(test_dataset).flatten().tolist()
btcTest["Model"] = predictions

# Save btcTest to CSV at models/model0.csv:
btcTest.to_csv("models/model0.csv")
