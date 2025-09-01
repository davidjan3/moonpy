from backtesting import Backtest, Strategy
import pandas as pd
import pandas_ta as ta
import util as ut

commission = 0.0


class SMACross(Strategy):
	n_fast = 20
	n_slow = 60

	def init(self):
		close = pd.Series(self.data.Close, name="Close")

		def _sma(series: pd.Series, length: int):
			out = ta.sma(series, length)
			if out is None or len(out) != len(series):
				return series.rolling(length).mean().to_numpy()
			return out.to_numpy()

		self.sma_fast = self.I(_sma, close, self.n_fast)
		self.sma_slow = self.I(_sma, close, self.n_slow)

	def next(self):
		if ut.crossover(self.sma_fast, self.sma_slow):
			if self.position.is_short:
				self.position.close()
			if not self.position:
				self.buy()
		elif ut.crossunder(self.sma_fast, self.sma_slow):
			if self.position.is_long:
				self.position.close()
			if not self.position:
				self.sell()


cols = ["Time", "Open", "High", "Low", "Close", "Volume"]
aapl = pd.read_csv(
	"./data/AAPL_1min.txt",
	names=cols,
	header=None,
	parse_dates=["Time"],
)
aapl = aapl.set_index("Time").sort_index()
# Remove any duplicated timestamps just in case
aapl = aapl[~aapl.index.duplicated(keep="first")]

# Pick the last full calendar year present in the data
last_ts = aapl.index.max()
last_year = last_ts.year
period_start = f"{last_year}-01-01"
period_end = f"{last_year}-12-31"
period = aapl.loc[period_start:period_end]

# Fallback: if slice empty (partial last year), use entire dataset
if period.empty:
	period = aapl
	print("Selected entire dataset (year slice empty)")
else:
	print(f"Using period {period_start} to {period_end} with {len(period)} rows")

bt = Backtest(period, SMACross, cash=10_000, commission=commission)
stats = bt.run()
print(stats)

# Plot entire period compressed to hourly bars (keeps year span & <=10k candles)
plot_freq = '1H'
plot_df = period.resample(plot_freq).agg({
	'Open': 'first',
	'High': 'max',
	'Low': 'min',
	'Close': 'last',
	'Volume': 'sum'
}).dropna()
print(f"Plotting full period aggregated to {plot_freq} with {len(plot_df)} rows (original {len(period)})")
bt_plot = Backtest(plot_df, SMACross, cash=10_000, commission=commission)
bt_plot.run()
bt_plot.plot(
	filename="plots/plotAAPL.html",
	open_browser=True,
	plot_drawdown=True,
	plot_return=True,
	plot_equity=False,
	resample=False,
)
