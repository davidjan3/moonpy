import yfinance as yf

btc = yf.Ticker("BTC")
history = btc.history("2y", "1h")
history.plot()
history.to_csv("./btc_1min.csv")