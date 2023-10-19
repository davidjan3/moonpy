import pandas as pd
import pandas_ta as ta
import util as ut
from backtesting import Backtest, Strategy


prevamount = 10000
commission = 0.005699 / 100  # Binance BTC: 0.005699 / 100


class Plot(Strategy):
    # Amount
    n_maxAmount = 0.5
    # Bollinger Bands
    n_bbLen = 30
    n_bbScale = 2.0
    # TP/SL
    n_tpThres = 1.5
    n_slThres = 0.5

    def init(self):
        open = pd.Series(self.data.Open)
        close = pd.Series(self.data.Close)
        high = pd.Series(self.data.High)
        low = pd.Series(self.data.Low)
        volume = pd.Series(self.data.Volume)
        model = pd.Series(self.data.Model)

        self.I(ta.sma, model, 1)
        # Bollinger Bands
        self.bb = self.I(
            ut.bbandsLMH, close, self.n_bbLen, self.n_bbScale, overlay=True
        )

    def next(self):
        open = self.data.Open[-1]
        high = self.data.High[-1]
        low = self.data.Low[-1]
        close = self.data.Close[-1]
        buydec = self.data.Model[-1]

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

        if amount < -0.05:  # and bbW > 0:
            # if self.position.is_short:
            #     self.position.close()
            self.buy(size=-amount * self.n_maxAmount, tp=l_tp, sl=l_sl)
        elif amount > 0.05:  # and bbW > 0:
            # if self.position.is_long:
            #     self.position.close()
            self.sell(size=amount * self.n_maxAmount, tp=s_tp, sl=s_sl)


def plot(df, plotNum):
    bt = Backtest(
        df,
        Plot,
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
        resample=True,
    )
