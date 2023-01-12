from backtesting import Backtest, Strategy
import pandas_ta as ta
import pandas as pd
import util as ut

import warnings
warnings.filterwarnings("ignore")

commission = 0.005699 / 100  # Binance BTC: 0.005699 / 100
prevamount = 10000
plotNum = 0


class MACDAction(Strategy):
    # MACD
    n_macdFast = 10
    n_macdSlow = 30
    n_macdSignal = 15
    # ATR
    n_atrLen = 30
    n_atrThres = 1.5
    n_atrSmaLen = 60*12
    n_atrSmaThres = 0.18
    # Bollinger Bands
    n_bbLen = 30
    n_bbScale = 2
    # Trend Filter
    b_tfUse = False
    n_tfLong = 240
    n_tfShort = 2
    # Volume Filter
    b_vfUse = False
    n_vfLong = 60*12
    n_vfShort = 5
    # TP/SL
    n_tpThres = 1.2
    n_slThres = 0.6
    # Amount
    n_amount = 0.99

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
        self.atrLong = self.I(ta.sma, ta.atr(
            high, low, close, self.n_atrLen*2, percent=True), self.n_atrSmaLen)
        # Bollinger Bands
        self.bb = self.I(ut.bbands, close, self.n_bbLen,
                         self.n_bbScale, overlay=True)
        # Trend Filter
        if self.b_tfUse:
            self.tfLong = self.I(ta.sma, close, self.n_tfLong, plot=False)
            self.tfShort = self.I(ta.ema, close, self.n_tfShort, plot=False)
        # Volume Filter
        if self.b_vfUse:
            self.vfLong = self.I(ta.sma, volume, self.n_vfLong, plot=False)
            self.vfShort = self.I(ta.ema, volume, self.n_vfShort, plot=False)

    def next(self):
        close = self.data.Close[-1]
        # MACD
        macd = self.macd[0]
        signal = self.macd[2]
        cl_macd = macd[-1] < 0 and ut.crossover(macd, signal)
        cs_macd = macd[-1] > 0 and ut.crossunder(macd, signal)
        # ATR
        c_atr = self.atr[-1] > abs(macd[-1]) * \
            self.n_atrThres
        # Bollinger Bands
        bbL = self.bb[0][-1]
        bbM = self.bb[1][-1]
        bbH = self.bb[2][-1]
        bbW = bbH - bbL
        cl_bb = close > bbL and close < bbM
        cs_bb = close < bbH and close > bbM
        # Trend Filter
        cl_tf = (not self.b_tfUse) or (
            close < self.tfLong[-1] and close > self.tfShort[-1])
        cs_tf = (not self.b_tfUse) or (
            close > self.tfLong[-1] and close < self.tfShort[-1])
        # Volume Filter
        c_vf = (not self.b_vfUse) or self.vfShort[-1] > self.vfLong[-1]
        # TP/SL
        l_close = (close * (1 + commission))
        s_close = (close * (1 - commission))
        l_tp = (l_close + bbW * self.n_tpThres)
        s_tp = (s_close - bbW * self.n_tpThres)
        l_sl = (l_close - bbW * self.n_slThres)
        s_sl = (s_close + bbW * self.n_slThres)
        # cl_bb = cl_bb and l_close < bbM and s_close > bbL
        # cs_bb = cs_bb and s_close > bbM and l_close < bbH

        amount = min(self.atrLong[-1] / self.n_atrSmaThres, 0.999)

        if cl_macd and c_atr and cl_bb and cl_tf and c_vf and amount > 0.25:
            self.buy(size=amount, tp=l_tp, sl=l_sl)
        elif cs_macd and c_atr and cs_bb and cs_tf and c_vf and amount > 0.25:
            self.sell(size=amount, tp=s_tp, sl=s_sl)


btc = pd.read_csv("./data/mBTC.csv")
btc['Time'] = pd.to_datetime(btc['Time'], unit='s')
btc = btc.set_index("Time").sort_index()
btcPeriod = btc.loc["2017-01-01":"2022-12-31"]

bt = Backtest(btcPeriod, MACDAction,
              cash=prevamount,
              commission=commission,
              )


# run = bt.run()
# print(run)

# bt.plot(filename="plots/plot" + str(plotNum),
#         open_browser=True, plot_drawdown=True, plot_return=True, plot_equity=False)

stats, heatmap = bt.optimize(
    n_macdFast=range(4, 60, 1),
    n_macdSlow=range(20, 120, 5),
    n_macdSignal=range(4, 60, 1),
    n_atrLen=range(4, 60, 1),
    n_atrThres=[x*0.1 for x in range(8, 25, 1)],
    n_atrSmaLen=range(60, 60*24, 60),
    n_atrSmaThres=[x*0.01 for x in range(8, 25, 1)],
    n_bbLen=range(4, 60, 1),
    n_bbScale=[x*0.1 for x in range(12, 25, 1)],
    n_tpThres=[x*0.1 for x in range(6, 25, 1)],
    n_slThres=[x*0.1 for x in range(6, 25, 1)],
    n_amount=[x*0.01 for x in range(49, 99, 5)],
    maximize="Equity Final [$]",
    method="skopt",
    # max_tries=150,
    return_heatmap=True,
)

print(stats)
print(stats._strategy)

# MACDAction(n_macdFast=6,n_macdSlow=72,n_macdSignal=4,n_atrLen=55,n_atrThres=0.8050596595548678,n_atrSmaLen=538,n_atrSmaThres=0.18758488822161595,n_bbLen=17,n_bbScale=1.5485865058216945,n_tpThres=1.0696466751789813,n_slThres=1.0130311738933546,n_amount=0.530247908429058) => 61438918.406185

"""
retSum = 0
posSum = 0
negSum = 0

for year in range(2017, 2023):
    for month in range(1, 13):
        lastday = ca.monthrange(year, month)[1]
        period = str(year)+"-"+str(month)
        start = period+"-01"
        end = period+f"-{lastday}"
        btcPeriod = btc.loc[start:end]
        bt = Backtest(btcPeriod, MACDAction,
                      cash=prevamount,
                      commission=commission,
                      )
        run = bt.run()
        newamount = run._equity_curve["Equity"][-1]
        # print(run)
        ret = 100*(newamount/prevamount - 1)
        retSum += ret
        if ret > 0:
            posSum += 1
        else:
            negSum += 1

        print(
            f"{end}:   \t${round(newamount, 2)} ({round(ret, 2)}%)   \t{run._trades.size} Trades")
        # print(run._trades)
        if (prevamount > newamount and plotLosses):
            bt.plot(filename="plots/" + period, open_browser=False)
        prevamount = newamount

print(f"P Total: {posSum + negSum}   P Pos: {posSum} ({round(100*posSum/(posSum+negSum), 2)}%)   P Neg: {negSum} ({round(100*negSum/(posSum+negSum),2)}%)   Avg: {round(retSum/(posSum+negSum), 2)}%")

"""
