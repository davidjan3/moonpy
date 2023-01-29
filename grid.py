from backtesting import Backtest, Strategy
import pandas_ta as ta
import pandas as pd
import util as ut

import warnings
warnings.filterwarnings("ignore")

commission = 0.0  # 0.005699 / 100  # Binance BTC: 0.005699 / 100
prevamount = 10000
plotNum = 1


class MACDAction(Strategy):
    # ADX
    n_adx = 60*6
    n_adxTema = 30
    n_adxLow = 10
    n_adxHigh = 15
    # Bollinger Bands
    n_bbLen = 60*12
    n_bbScale = 3.0
    # Trend Filter
    n_tfLong = 60*12
    n_tfShort = 60
    n_tfReduct = 0.5
    # TP/SL
    n_tpThres = 1.4
    n_slThres = 0.4
    # Amount
    n_maxAmount = 0.1

    def init(self):
        open = pd.Series(self.data.Open)
        close = pd.Series(self.data.Close)
        high = pd.Series(self.data.High)
        low = pd.Series(self.data.Low)
        volume = pd.Series(self.data.Volume)

        # ADX
        self.adx = self.I(ta.tema, ut.adx(
            high, low, close, self.n_adx), self.n_adxTema)
        # Bollinger Bands
        self.bb1 = self.I(ut.bbandsLH, close, self.n_bbLen,
                          self.n_bbScale * (1/10), overlay=True)
        self.bb2 = self.I(ut.bbandsLH, close, self.n_bbLen,
                          self.n_bbScale * (3/10), overlay=True)
        self.bb3 = self.I(ut.bbandsLH, close, self.n_bbLen,
                          self.n_bbScale * (7/10), overlay=True)
        self.bb4 = self.I(ut.bbandsLH, close, self.n_bbLen,
                          self.n_bbScale * (10/10), overlay=True)
        # Trend Filter
        self.tfLong = self.I(ta.sma, close, self.n_tfLong, plot=False)
        self.tfShort = self.I(ta.ema, close, self.n_tfShort, plot=False)

    def next(self):
        l_amount = 0
        s_amount = 0

        barIndex = self._broker._i
        close = self.data.Close
        # ADX
        adx = self.adx[-1]
        c_adx = True  # adx < 8
        # Bollinger Bands
        index = 0
        if ut.crossunder(close, self.bb4[0]):
            index = 4
        elif ut.crossunder(close, self.bb3[0]):
            index = 3
        elif ut.crossunder(close, self.bb3[0]):
            index = 2
        elif ut.crossunder(close, self.bb3[0]):
            index = 1

        if ut.crossover(close, self.bb4[1]):
            index = -4
        elif ut.crossover(close, self.bb3[1]):
            index = -3
        elif ut.crossover(close, self.bb2[1]):
            index = -2
        elif ut.crossover(close, self.bb1[1]):
            index = -1

        if index > 0:
            l_amount = self.n_maxAmount * (index / 4)
        elif index < 0:
            s_amount = self.n_maxAmount * (-index / 4)

        # # Trend Filter
        # tfMult = 1.0 - adxStrength * self.n_tfReduct
        # if (self.tfShort[-1] < self.tfLong[-1]):
        #     l_amount *= tfMult
        # if (self.tfShort[-1] > self.tfLong[-1]):
        #     s_amount *= tfMult
        # TP/SL
        bbW = self.bb4[1][-1] - self.bb4[0][-1]
        c_bbW = bbW < close[-1]*0.025
        l_close = (close[-1] * (1 + commission))
        s_close = (close[-1] * (1 - commission))
        l_tp = (l_close + bbW * self.n_tpThres)
        s_tp = (s_close - bbW * self.n_tpThres)
        l_sl = (l_close - bbW * self.n_slThres)
        s_sl = (s_close + bbW * self.n_slThres)

        if l_amount > 0 and c_adx and c_bbW:
            # self.closeTrades(False)
            self.buy(size=l_amount, tp=l_tp, sl=l_sl)
        elif s_amount > 0 and c_adx and c_bbW:
            # self.closeTrades(True)
            self.sell(size=s_amount, tp=s_tp, sl=s_sl)

    def closeTrades(self, direction):
        for trade in self.trades:
            if trade.is_long and direction:
                trade.close()
            elif trade.is_short and not direction:
                trade.close()


btc = pd.read_csv("./data/mBTC.csv")
btc['Time'] = pd.to_datetime(btc['Time'], unit='s')
btc = btc.set_index("Time").sort_index()
btcPeriod = btc.loc["2017-01-01":"2022-12-31"]

bt = Backtest(btcPeriod, MACDAction,
              cash=prevamount,
              commission=commission,
              )


run = bt.run()
print(run)

bt.plot(filename="plots/plot" + str(plotNum),
        open_browser=True, plot_drawdown=True, plot_return=True, plot_equity=False, resample=True)

# stats = bt.optimize(
#     n_macdFast=range(4, 60, 1),
#     n_macdSlow=range(20, 120, 5),
#     n_macdSignal=range(4, 60, 1),
#     n_atrLen=range(4, 60, 1),
#     n_atrThres=[x*0.1 for x in range(8, 25, 1)],
#     n_atrSmaLen=range(60, 60*24, 60),
#     # n_atrSmaThres=[x*0.01 for x in range(8, 25, 1)],
#     n_bbLen=range(4, 60, 1),
#     n_bbScale=[x*0.1 for x in range(12, 25, 1)],
#     n_tpThres=[x*0.1 for x in range(6, 25, 1)],
#     n_slThres=[x*0.1 for x in range(6, 25, 1)],
#     n_amount=[x*0.01 for x in range(49, 99, 5)],
#     # maximize="Equity Final [$]",
#     method="skopt",
#     max_tries=50,
# )

# print(stats)
# print(stats._strategy)

# MACDAction(n_macdFast=6,n_macdSlow=72,n_macdSignal=4,n_atrLen=55,n_atrThres=0.8050596595548678,n_atrSmaLen=538,n_atrSmaThres=0.18758488822161595,n_bbLen=17,n_bbScale=1.5485865058216945,n_tpThres=1.0696466751789813,n_slThres=1.0130311738933546,n_amount=0.530247908429058) => 61438918.406185
# MACDAction(n_macdFast=43,n_macdSlow=61,n_macdSignal=49,n_atrLen=34,n_atrThres=2.113860864909628,n_atrSmaLen=406,n_bbLen=40,n_bbScale=1.7063145112532396,n_tpThres=1.2745501489663749,n_slThres=0.7188151317694774,n_amount=0.5081633964851199) => 228.590968% in 2019
# MACDAction(n_macdFast=32,n_macdSlow=79,n_macdSignal=48,n_atrLen=57,n_atrThres=1.623723638595235,n_atrSmaLen=1021,n_bbLen=16,n_bbScale=1.6020904012484685,n_tpThres=1.1455855778001234,n_slThres=1.1691821479133113,n_amount=0.6197515454828277) => SQN 4.95, Sharpe 1.88

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
