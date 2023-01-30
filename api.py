from os import getenv
from binance import Client
import pandas as pd


class API:
    api_key = getenv("BINANCE_KEY")
    api_secret = getenv("BINANCE_SECRET")
    market = "BTCUSDT"

    def __init__(self):
        self.client = Client(self.api_key, self.api_secret)
        print("Connected at server time:\t", self.getServerTime())

    def getServerTime(self):
        return self.client.get_server_time()["serverTime"]

    def getHistdata(self, minutesBack):
        endTs = pd.Timestamp(self.getServerTime(), unit="ms").floor(
            freq="T") - pd.Timedelta(minutes=1)
        startTs = endTs - pd.Timedelta(minutes=minutesBack)
        endTsStr = str(int(endTs.timestamp())*1000)
        startTsStr = str(int(startTs.timestamp())*1000)
        klines = self.client.get_historical_klines(
            self.market, Client.KLINE_INTERVAL_1MINUTE, startTsStr, endTsStr)
        return API.binance2Df(klines)

    def binance2Df(klines):
        klines = [[round(line[0]/1000), line[1], line[2], line[3], line[4], line[5]]
                  for line in klines]
        df = pd.DataFrame(
            klines, columns=["Time", "Open", "High", "Low", "Close", "Volume"])
        df = df.astype({
            "Open": float,
            "High": float,
            "Low": float,
            "Close": float,
            "Volume": float
        })
        df['Time'] = pd.to_datetime(df['Time'], unit='s')
        df = df.set_index("Time").sort_index()
        return df
