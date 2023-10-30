import tensorflow as tf
import pandas as pd
import ai_util as ut
import ai_plot as plot

INPUT_LEN = 4

print("Loading model...")
model = tf.keras.models.load_model("models/model9.keras")

print("Loading CSV...")
btc = pd.read_csv("./data/pData_idx.csv")
btc["Time"] = pd.to_datetime(btc["Time"], unit="s")
btc = btc.set_index("Time")
btcTest = btc.loc["2019-06-01":"2019-12-31"]
btcTest = btcTest.dropna()
x_test, y_test = ut.makeSets(btcTest, INPUT_LEN)
btcTestDS = ut.toDataset(x_test, y_test).batch(4096)

print("Predicting...")
btcTest = btcTest.iloc[:, :5]
prediction = model.predict(btcTestDS)
predictions = [0 for i in range(INPUT_LEN - 1)] + prediction.flatten().tolist()
btcTest["Model"] = predictions
btcTest["Model"] = ut.normalizeMinMaxSplitZero(btcTest["Model"])

print("Plotting...")
plot.plot(btcTest, 9)
