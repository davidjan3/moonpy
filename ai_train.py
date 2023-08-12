# import os
# os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
# os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

import pandas as pd
import tensorflow as tf

model = tf.keras.models.Sequential(
    [
        tf.keras.layers.Input(shape=(1, 2 * 15)),
        tf.keras.layers.Dense(16, activation=tf.keras.activations.tanh),
        tf.keras.layers.Dense(8, activation=tf.keras.activations.tanh),
        tf.keras.layers.Dense(2, activation=tf.keras.activations.tanh),
        tf.keras.layers.Dense(1, activation=tf.keras.activations.tanh),
    ]
)

model.compile(
    optimizer=tf.keras.optimizers.RMSprop(0.001),
    loss=tf.keras.losses.MeanAbsoluteError(),
)


def makeSets(data):
    print("Normalizing...")
    dataX = data.iloc[:, 0:15]
    dataX = (dataX - dataX.min()) / (dataX.max() - dataX.min())
    dataXArr = dataX.values.tolist()

    print("Preparing training data...")
    x_train = [[dataXArr[i - 1] + dataXArr[i]] for i in range(1, len(dataXArr))]
    y_train = data.iloc[:, 15].values.tolist()[1:]

    return x_train, y_train


print("Loading CSV...")
btc = pd.read_csv("./data/mBTC_idx.csv")
btc["Time"] = pd.to_datetime(btc["Time"], unit="s")
btc = btc.set_index("Time")
btcTrain = btc.loc["2020-01-01":"2020-01-02"]
btcTest = btc.loc["2020-01-02":"2020-01-03"]
x_train, y_train = makeSets(btcTrain)
x_test, y_test = makeSets(btcTest)

# Create train dataset and call model.fit with it:
print("Creating train dataset...")
train_dataset = tf.data.Dataset.from_tensor_slices((x_train, y_train))
train_dataset = train_dataset.shuffle(buffer_size=1024).batch(64)

print("Pretesting on trainset:")
model.evaluate(train_dataset, verbose=2)

print("Pretesting on testset:")
# model.evaluate(x_test, y_test, verbose=2)

print("Training...")
model.fit(train_dataset, epochs=50)
model.save_weights("models/weights000")

print("Testing on trainset:")
model.evaluate(train_dataset, verbose=2)

print("Testing on testset:")
# model.evaluate(x_test, y_test, verbose=2)
