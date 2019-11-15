import websocket
import ssl
import json
import time
from datetime import datetime
import requests
import os
import yaml

ws = websocket.WebSocket(sslopt={'cert_reqs': ssl.CERT_NONE})

#ws.connect('wss://www.bitmex.com/realtime?subscribe=tradeBin1m:XBTUSD')
#ws.connect('wss://www.bitmex.com/realtime?subscribe=tradeBin1m:XBTUSD,tradeBin5m:XBTUSD,trade:XBTUSD')

r = requests.get('https://www.bitmex.com/api/v1/trade/bucketed?binSize=1h&partial=false&symbol=XBTUSD&count=2&reverse=true')
d = r.json()
print(d)

# OPEN INTEREST UPDATES
# ws.connect('wss://www.bitmex.com/realtime?subscribe=instrument:XBTUSD')
# count = 0
# #start = time.time()
# while count < 5:
#   print(datetime.utcfromtimestamp(int(time.time()) + 3600).strftime('%Y-%m-%d %H:%M:%S'))
#   res = ws.recv()
#   res = json.loads(res)
#   if 'table' in res.keys() and res['table'] == 'instrument' and res['action'] == 'partial':
#       print(res['data'][0]['openInterest'])
#       count += 1
#   if 'table' in res.keys() and res['table'] == 'instrument' and res['action'] == 'update':
#       for update in res['data']:
#           if 'openInterest' in update.keys():
#               print(update['openInterest'])
#               #print(time.time() - start)
#               #start = time.time()
#               count += 1

# FUNDING RATE
# ws.connect('wss://www.bitmex.com/realtime?subscribe=instrument:XBTUSD')
# count = 0
# #start = time.time()
# while count < 5:
#   res = ws.recv()
#   res = json.loads(res)
#   if 'table' in res.keys() and res['table'] == 'instrument' and res['action'] == 'partial':
#       print(res['data'][0]['fundingRate'])
#       count += 1
#   if 'table' in res.keys() and res['table'] == 'instrument' and res['action'] == 'update':
#       for update in res['data']:
#           if 'fundingRate' in update.keys():
#               print(update['fundingRate'])
#               #print(time.time() - start)
#               #start = time.time()
#               count += 1

# INDICATIVE FUNDING RATE
# ws.connect('wss://www.bitmex.com/realtime?subscribe=instrument:XBTUSD')
# count = 0
# #start = time.time()
# while count < 5:
#   res = ws.recv()
#   res = json.loads(res)
#   if 'table' in res.keys() and res['table'] == 'instrument' and res['action'] == 'partial':
#       print(res['data'][0]['indicativeFundingRate'])
#       count += 1
#   if 'table' in res.keys() and res['table'] == 'instrument' and res['action'] == 'update':
#       for update in res['data']:
#           if 'indicativeFundingRate' in update.keys():
#               print(update['indicativeFundingRate'])
#               #print(time.time() - start)
#               #start = time.time()
#               count += 1

# 1m VOLUME CHANGE
# ws.connect('wss://www.bitmex.com/realtime?subscribe=tradeBin5m:XBTUSD')
# count = 0
# previous = 0
# while count < 50:
#   res = ws.recv()
#   res = json.loads(res)
#   if 'table' in res.keys() and res['table'] == 'tradeBin5m' and res['action'] in ['partial', 'insert']:
#       print(datetime.utcfromtimestamp(int(time.time()) + 3600).strftime('%Y-%m-%d %H:%M:%S'))
#       print('1m Volume:\t' + format(res['data'][0]['volume'], ","))
#       if previous > 0:
#         sign = '+' if res['data'][0]['volume'] > previous else ''
#         print('1m USD Volume Change\t\t' + sign + format(res['data'][0]['volume'] - previous, ",") + ' USD (' + sign + str(round(100 * (res['data'][0]['volume'] - previous) / previous, 2)) + '%)')
#       print()
#       previous = res['data'][0]['volume']
#       count += 1





