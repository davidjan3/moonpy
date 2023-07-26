from api import API

api = API()
print("Getting data...")
btcPeriod = api.getHistdata(120 * 24 * 45)
btcPeriod.to_csv("data/mBTC_Temp.csv")
print("Got data")
