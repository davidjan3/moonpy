import pandas_ta as ta
import pandas as pd
import ai_util as ut

btc = pd.read_csv("./data/mBTC.csv")
btc = btc.set_index("Time")
open = btc["Open"]
close = btc["Close"]
high = btc["High"]
low = btc["Low"]

macd = ta.macd(close, 10, 30, 15)
btc["MACDVal"] = macd.iloc[:, 0]
btc["MACDSignal"] = macd.iloc[:, 2]

atr = ta.atr(high, low, close, 30)
btc["ATR"] = atr
btc["ATRSMAShort"] = ta.sma(atr, 60 * 12)
btc["ATRSMALong"] = ta.sma(atr, 60 * 24 * 7)

btc["ADX"] = ta.tema(ut.adx(high, low, close, 60), 30)

bb = ut.bbandsLMH(close, 30, 2.0)
btc["BBLower"] = bb.iloc[:, 0]
btc["BBMiddle"] = bb.iloc[:, 1]
btc["BBUpper"] = bb.iloc[:, 2]

btc["TFLong"] = ta.sma(close, 60 * 24)
btc["TFShort"] = ta.sma(close, 60)

btc["Buydec"] = close.rolling(29).apply(ut.buydec).shift(-14)

btc.to_csv("./data/mBTC_idx.csv")
