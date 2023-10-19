import tensorflow as tf
import pandas as pd
import ai_util as ut
import ai_plot as plot

INPUT_LEN = 4

print("Loading model...")
model = tf.keras.models.load_model("models/model6.keras")

print("Loading CSV...")
btc = pd.read_csv("./data/mBTC_idx_2022.csv")
btc["Time"] = pd.to_datetime(btc["Time"])  # , unit="s")
btc = btc.set_index("Time")
btcTest = btc  # .loc["2019-01-01":"2020-01-31"]
btcTest = btcTest.dropna()
x_test, y_test = ut.makeSets(btcTest, INPUT_LEN)
btcTestDS = ut.toDataset(x_test, y_test).batch(4096)

print("Predicting...")
btcTest = btcTest.iloc[:, :5]
prediction = model.predict(btcTestDS)
predictions = [0 for i in range(INPUT_LEN - 1)] + prediction.flatten().tolist()
btcTest["Model"] = predictions

print(btcTest)

print("Plotting...")
plot.plot(btcTest, 7)
