import binance

# res = binance.send_public_request('/api/v3/klines', {'symbol': 'BTCUSDT', 'interval': str(5) + 'm', 'limit': 2})

# response = binance.send_signed_request('GET', '/api/v3/account')
# btc_qty = float(response['balances'][0]['free'])

# 있는거 다팔게
# print(res)
# params = {
#             "symbol": 'BTCUSDT',
#             "side": "SELL",
#             "type": "MARKET",
#             "quantity": 0.00110,
#         }

params = {
            "symbol": 'BTCUSDT',
            "side": "BUY",
            "type": "STOP_LOSS",
            "quoteOrderQty": 12,
            "stopPrice": 10000
        }
response = binance.send_signed_request('POST', '/api/v3/order', params)


print(response)