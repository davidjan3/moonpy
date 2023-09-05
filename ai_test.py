import tensorflow as tf
import pandas as pd
import ai_util as ut
import ai_plot as plot

print("Loading model...")
model = tf.keras.models.load_model("models/model2.keras")

print("Loading CSV...")
btc = pd.read_csv("./data/mBTC_idx.csv")
btc["Time"] = pd.to_datetime(btc["Time"], unit="s")
btc = btc.set_index("Time")
btcTest = btc.loc["2019-01-01":"2021-12-31"]
btcTest = btcTest.dropna()
x_test, y_test = ut.makeSets(btcTest)
btcTestDS = ut.toDataset(x_test, y_test)

print("Predicting...")
btcTest = btcTest.iloc[:, :5]
predictions = [0] + model.predict(btcTestDS).flatten().tolist()
btcTest["Model"] = predictions

print("Plotting...")
plot.plot(btcTest, 4)
