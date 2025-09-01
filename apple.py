from backtesting import Backtest, Strategy
import pandas as pd


class MiniSMA(Strategy):
	n = 50

	def init(self):
		def _sma(arr, n):
			return pd.Series(arr).rolling(n).mean()
		self.sma = self.I(_sma, self.data.Close, self.n)

	def next(self):
		price = self.data.Close[-1]
		avg = self.sma[-1]
		if pd.isna(avg):
			return
		if not self.position and price > avg:
			self.buy()
		elif self.position and price < avg:
			self.position.close()


cols = ["Time", "Open", "High", "Low", "Close", "Volume"]
data = pd.read_csv(
	"./data/AAPL_1min.txt",
	names=cols,
	header=None,
	parse_dates=["Time"],
).set_index("Time")
data = data[~data.index.duplicated(keep="first")]

bt = Backtest(data, MiniSMA, cash=10_000, commission=0.0)
stats = bt.run()
print(stats[['Return [%]', 'Equity Final [$]', '# Trades']])

# Plot on downsampled data to avoid excessive candles and index conversion issues
plot_df = data.resample('1H').agg({
	'Open': 'first',
	'High': 'max',
	'Low': 'min',
	'Close': 'last',
	'Volume': 'sum'
}).dropna()
bt_plot = Backtest(plot_df, MiniSMA, cash=10_000, commission=0.0)
bt_plot.run()
bt_plot.plot(
	filename="plots/plotAAPL_minimal.html",
	open_browser=True,
	plot_equity=True,
	plot_return=True,
	plot_drawdown=True,
	resample=False,
)
