import ai_plot as plot
import pandas as pd
import ai_util as ut

print("Loading CSV...")
df = pd.read_csv("./data/pData_idx.csv")
df["Time"] = pd.to_datetime(df["Time"], unit="s")
df = df.set_index("Time")
df = df.loc["2019-01-01":"2019-01-31"]
df = df.dropna()
df = df.rename(columns={"Buydec": "Model"})
df["Model"] = ut.normalizeMinMaxSplitZero(df["Model"])

print("Plotting...")
plot.plot(df, 9)
