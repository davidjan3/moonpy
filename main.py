from backtesting import Backtest, Strategy
from backtesting.lib import crossover

from backtesting.test import SMA, GOOG
import pandas_ta as ta
import pandas as pd
import util as ut


class SmaCross(Strategy):
    # MACD
    n_macdFast = 10
    n_macdSlow = 30
    n_macdSignal = 15
    # ATR
    n_atrLen = 30
    n_atrThres = 1.0
    # Trend Filter
    b_tfUse = False
    n_tfLong = 240
    n_tfShort = 2
    # Volume Filter
    b_vfUse = False
    n_vfLong = 120
    n_vfShort = 15

    def init(self):
        open = pd.Series(self.data.Open)
        close = pd.Series(self.data.Close)
        high = pd.Series(self.data.High)
        low = pd.Series(self.data.Low)
        volume = pd.Series(self.data.Volume)

        # MACD
        self.macd = self.I(ta.macd, close, self.n_macdFast,
                           self.n_macdSlow, self.n_macdSignal)
        # ATR
        self.atr = self.I(ta.atr, high, low, close, self.n_atrLen)
        # Trend Filter
        self.tfLong = self.I(ta.sma, close, self.n_tfLong)
        self.tfShort = self.I(ta.ema, close, self.n_tfShort)
        # Volume Filter
        self.vfLong = self.I(ta.sma, close, self.n_vfLong)
        self.vfShort = self.I(ta.ema, close, self.n_vfShort)

    def next(self):
        close = self.data.Close[-1]

        # MACD
        macd = self.macd[0]
        macdChange = macd[-1] - macd[-2]
        signal = self.macd[2]
        hist = self.macd[1]
        cl_macd = macd < 0 and ut.crossover(macd, signal)
        cs_macd = macd > 0 and ut.crossunder(macd, signal)
        # ATR
        c_atr = self.atr > macd * self.n_atrThres
        # Trend Filter
        cl_tf = (not self.b_tfUse) or (
            close < self.tfLong and close > self.tfShort)
        cs_tf = (not self.b_tfUse) or (
            close > self.tfLong and close < self.tfShort)
        # Volume Filter
        c_vf = (not self.b_vfUse) or self.vfShort > self.vfLong

        if cl_macd and c_atr and cl_tf and c_vf:
            self.buy()
        elif cs_macd and c_atr and cs_tf and c_vf:
            self.sell()


btc = pd.read_csv("./data/mBTC.csv")
btc['Time'] = pd.to_datetime(btc['Time'], unit='s')
btc = btc.set_index("Time")
btc = btc.loc["2020-01-01": "2020-01-02"]

bt = Backtest(btc, SmaCross,
              cash=10000, commission=0.002,
              exclusive_orders=True)

bt.run()
bt.plot()

# stats = bt.optimize(n_macdFast=range(5, 60, 5),
#                     n_macdSlow=range(20, 360, 10),
#                     n_macdSignal=range(5, 60, 5),
#                     n_atrLen=range(5, 60, 5),
#                     constraint=lambda p: p.n_macdFast < p.n_macdSlow and p.n_macdSignal < p.n_macdSlow,
#                     maximize='Equity Final [$]',
#                     return_heatmap=True)
# print(stats)

# bt.run()
# bt.plot()

"""
# Import necessary libraries
import pandas as pd
import numpy as np

# Load data for desired cryptocurrency
data = pd.read_csv('crypto_data.csv')

# Calculate moving average and standard deviation
ma = data['Close'].rolling(window=20).mean()
std = data['Close'].rolling(window=20).std()

# Create buy and sell signals based on Bollinger bands
data['Upper Band'] = ma + (std * 2)
data['Lower Band'] = ma - (std * 2)
data['Buy Signal'] = np.where(data['Close'] < data['Lower Band'], 1, 0)
data['Sell Signal'] = np.where(data['Close'] > data['Upper Band'], 1, 0)

# Implement buy and sell signals
for i in range(len(data)):
  if data['Buy Signal'][i] == 1:
    # Place buy order
    pass
  elif data['Sell Signal'][i] == 1:
    # Place sell order
    pass
  else:
    # Do not place any orders
    pass
"""
