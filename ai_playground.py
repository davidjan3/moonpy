from backtesting import Backtest, Strategy
import pandas_ta as ta
import pandas as pd
import util as ut
import warnings

warnings.filterwarnings("ignore")

btc = pd.read_csv("./data/mBTC2.csv")
btc["Time"] = pd.to_datetime(btc["Time"], unit="s")
btc = btc.set_index("Time")
btcPeriod = btc.loc["2022-01-01":"2022-01-31"]
btcPeriod["Buydec"] = btcPeriod["Close"].rolling(29).apply(ut.buydec).shift(-14)
print(btcPeriod.to_string())

# btc = pd.read_csv("./data/mBTC_Jan.csv")
# btc["Time"] = pd.to_datetime(btc["Time"])  # , unit='s')
# btc = btc.set_index("Time").sort_index()
# btcPeriod = btc  # .loc["2017-01-01":"2022-12-31"]
# ut.millify(btcPeriod)

commission = 0.005699 / 100  # Binance BTC: 0.005699 / 100
prevamount = 10000
plotNum = 1


class MACDAction(Strategy):
    # MACD
    n_macdFast = 10
    n_macdSlow = 30
    n_macdSignal = 15
    # ATR
    n_atrLen = 30
    n_atrThres = 1.3333
    n_atrSmaShort = 60 * 12
    n_atrSmaLong = 60 * 24 * 7
    # ADX
    n_adx = 60
    n_adxTema = 30
    n_adxLow = 10
    n_adxHigh = 20
    # Bollinger Bands
    n_bbLen = 30
    n_bbScale = 2.0
    # Trend Filter
    n_tfLong = 60 * 24
    n_tfShort = 60 * 2
    n_tfReduct = 0.3333
    # TP/SL
    n_tpThres = 1.5
    n_slThres = 0.5
    # Amount
    n_maxAmount = 0.9999

    def init(self):
        open = pd.Series(self.data.Open)
        close = pd.Series(self.data.Close)
        high = pd.Series(self.data.High)
        low = pd.Series(self.data.Low)
        volume = pd.Series(self.data.Volume)
        buydec = pd.Series(self.data.Buydec)

        self.I(ta.sma, buydec, 1)

        # MACD
        self.macd = self.I(
            ta.macd, close, self.n_macdFast, self.n_macdSlow, self.n_macdSignal
        )
        # ATR
        self.atr = self.I(ta.atr, high, low, close, self.n_atrLen)
        self.atrSmaShort = self.I(
            ta.sma,
            ta.atr(high, low, close, self.n_atrLen * 2, percent=True),
            self.n_atrSmaShort,
        )
        self.atrSmaLong = self.I(
            ta.sma,
            ta.atr(high, low, close, self.n_atrLen * 2, percent=True),
            self.n_atrSmaLong,
        )
        # ADX
        self.adx = self.I(ta.tema, ut.adx(high, low, close, self.n_adx), self.n_adxTema)
        # Bollinger Bands
        self.bb = self.I(
            ut.bbandsLMH, close, self.n_bbLen, self.n_bbScale, overlay=True
        )
        # Trend Filter
        self.tfLong = self.I(ta.sma, close, self.n_tfLong, plot=False)
        self.tfShort = self.I(ta.ema, close, self.n_tfShort, plot=False)

    def next(self):
        open = self.data.Open[-1]
        high = self.data.High[-1]
        low = self.data.Low[-1]
        close = self.data.Close[-1]
        buydec = self.data.Buydec[-1]

        amount = buydec

        # Bollinger Bands
        bbL = self.bb[0][-1]
        bbM = self.bb[1][-1]
        bbH = self.bb[2][-1]
        bbW = bbH - bbL
        # TP/SL
        l_close = close * (1 + commission)
        s_close = close * (1 - commission)
        l_tp = l_close + bbW * self.n_tpThres
        s_tp = s_close - bbW * self.n_tpThres
        l_sl = l_close - bbW * self.n_slThres
        s_sl = s_close + bbW * self.n_slThres

        if amount > 0.5:  # and bbW > 0:
            if self.position.is_short:
                self.position.close()
            self.buy(size=amount * self.n_maxAmount)  # , tp=l_tp, sl=l_sl)
        elif amount < -0.5:  # and bbW > 0:
            if self.position.is_long:
                self.position.close()
            self.sell(size=-amount * self.n_maxAmount)  # , tp=s_tp, sl=s_sl)


bt = Backtest(
    btcPeriod,
    MACDAction,
    cash=prevamount,
    commission=commission,
)


run = bt.run()
print(run)

bt.plot(
    filename="plots/plot" + str(plotNum),
    open_browser=True,
    plot_drawdown=True,
    plot_return=True,
    plot_equity=False,
    resample=False,
)
