from api import API

api = API()
print("Getting data...")
btcPeriod = api.getHistdata(60*24*45)
btcPeriod.to_csv("data/mBTC_Jan.csv")
print("Got data")
