# Time,Open,High,Low,Close,Volume
import random
import pandas as pd

MAX_VELOCITY = 0.001
MAX_ACCEL = 0.00001
MIN_CLOSE = 10
MAX_CLOSE = 55

# Create dataset, define time as pd.date_range(start="2019-01-01", end="2019-12-31", freq="1min")
df = pd.DataFrame(
    {
        "Time": pd.date_range(start="2019-01-01", end="2019-12-31", freq="1min"),
        "Open": 0,
        "High": 0,
        "Low": 0,
        "Close": 0,
        "Volume": 0,
    }
)

# Iterate over dataset
last_close = 10
velocity = 0
accel = MAX_ACCEL * 0.1
last_switch = 10
for index, row in df.iterrows():
    if abs(velocity + accel) < MAX_VELOCITY:
        velocity += accel
    new_close = last_close + velocity
    df.loc[index, "Open"] = last_close
    df.loc[index, "Close"] = new_close
    df.loc[index, "High"] = new_close + random.random() * MAX_ACCEL * 5
    df.loc[index, "Low"] = new_close - random.random() * MAX_ACCEL * 5
    df.loc[index, "Volume"] = random.random() * 50000
    last_close = new_close

    if (
        (
            (accel > 0 and new_close > last_switch)
            or (accel < 0 and new_close < last_switch)
        )
        and random.random() > 0.95
    ) or (
        (velocity < 0 and new_close < MIN_CLOSE)
        or (velocity > 0 and new_close > MAX_CLOSE)
    ):
        last_switch = min(max(new_close, MIN_CLOSE), MAX_CLOSE)
        accelMult = (
            random.random() if new_close > MIN_CLOSE and new_close < MAX_CLOSE else 1
        )
        accel = -(velocity / abs(velocity)) * accelMult * MAX_ACCEL

# Convert time to unix timestamp
df["Time"] = df["Time"].astype("int64") // 10**9
print(df["Low"].min(), df["High"].max())
df.to_csv("data/pData.csv", index=False)
