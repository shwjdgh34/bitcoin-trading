import binance
from pandas import DataFrame, to_numeric
from datetime import datetime
'''
print(binance.send_signed_request('GET', '/api/v3/account'))
'''


class Market:
    def __init__(self, coin):
        self.ma20ma50 = 0
        self.maxPrice = 0
        self.coin = coin

    # TODO: ma20, ma50이 아니여도 ㄱㅊ도록 수정하기
    def goldenCrossed(self, ma20, ma50):
        ret = False
        if self.ma20ma50 < 0 and ma20 - ma50 > 0:
            ret = True

        self.ma20ma50 = ma20 - ma50
        return ret

    def getData(self, numOfData, interval, hold):
        # request => return df
        # ----------------------------------------------------------------------------
        candleData = {
            'open': [], 'high': [], 'low': [], 'close': [], 'volume': [], 'closeTime': []
        }
        index = []

        responses = binance.send_public_request(
            '/api/v3/klines', {'symbol': self.coin, 'interval': str(interval) + 'm', 'limit': numOfData})

        for res in responses:
            time = datetime.fromtimestamp(res[0]/1000)
            index.append(time)
            # candleData['openTime'].append()
            candleData['open'].append(res[1])
            candleData['high'].append(res[2])
            candleData['low'].append(res[3])
            candleData['close'].append(res[4])
            candleData['volume'].append(res[5])
            candleData['closeTime'].append(res[6])
        df = DataFrame(candleData, index=index)
        ma20 = df['close'].rolling(window=20).mean()
        ma50 = df['close'].rolling(window=50).mean()
        # TODO 구매한 시점부터의 max price
        if hold:
            self.maxPrice = max(self.maxPrice, to_numeric(df['close'][-1]))
        else:
            self.maxPrice = 0
        self.ma20ma50 = ma20-ma50
        return df
        # ----------------------------------------------------------------------------


class User:
    # fetch Account amount from binance
    def __init__(self):
        self.hold = False
        self.BTC = 0
        self.USDT = 0

    def buy(self, coin, usdTradeAmount, stopPrice):
        # # place an order
        # if you see order response, then the parameters setting is correct
        # TODO: try except
        # TODO: stop_loss 시도해보기
        params = {
            "symbol": coin,
            "side": "BUY",
            "type": "MARKET",
            "quoteOrderQty": usdTradeAmount,
        }
        response = binance.send_signed_request('POST', '/api/v3/order', params)
        # TODO
        # self.BTC = response['data']['BTC']
        print(response)
        return response

    def sell(self, coin):
        # TODO: try except
        params = {
            "symbol": coin,
            "side": "SELL",
            "type": "MARKET",
            "quantity": self.BTC,  # TODO 수수료 제외하기
        }
        response = binance.send_signed_request('POST', '/api/v3/order', params)
        print(response)


# ======== CONSTANT================
USD_TRADE_AMOUNT = 12  # 10 dollar
INTERVAL = 5  # 5m
DATA_NUM = 1000
STOP_LOSS = 0.97
ONE_HOUR_AGO_PRICE_PERCENTAGE = 1.05
GOLDEN_CROSS_PRICE_PERCENTAGE = 1.02

# ==========INIT====================
ONE_HOUR_ROW = int(60/INTERVAL)

user = User()
market = Market('BTCUSDT')

# while True:
df = market.getData(DATA_NUM, INTERVAL, user.hold)
ma20 = df['close'].rolling(window=20).mean()
ma50 = df['close'].rolling(window=50).mean()
ma120 = df['close'].rolling(window=120).mean()

curClosePrice = df['close'][-1]
print(df['close'])
oneHourAgoPrice = df['close'][-ONE_HOUR_ROW]

# # 매수
# user.buy('BTCUSDT',12, float(curClosePrice) * STOP_LOSS)

# 매수 알고리즘 ----------------------------------------------------------------------------------------------
if market.goldenCrossed(ma20[-1], ma50[-1]) and user.hold == False:
    goldenCrossPrice = (ma20[-1]+ma50[-1])/2
    # 매수 (2)조건 and
    if goldenCrossPrice > ma120 and curClosePrice > ma120:
        # 매수 (1) 조건 and
        if oneHourAgoPrice*ONE_HOUR_AGO_PRICE_PERCENTAGE >= curClosePrice and goldenCrossPrice*GOLDEN_CROSS_PRICE_PERCENTAGE > curClosePrice:
            try:
                user.buy('BTCUSDT', USD_TRADE_AMOUNT,
                         float(curClosePrice) * STOP_LOSS)
                user.hold = True
            except Exception as err:
                print("Error!! cant buy :", err)
# 매도 알고리즘-------------------------------------------------------------------------------------------------
elif user.hold == True:
    # TODO: 매도조건 (1)??
    # 매도조건 (2),(3)
    if market.maxPrice * 0.995 > curClosePrice or curClosePrice > ma20 * 1.2:
        # TODO: try except
        user.sell('BTCUSDT')
