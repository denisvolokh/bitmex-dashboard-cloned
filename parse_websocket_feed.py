
import websocket
import ssl
import json
import time
import datetime
import requests
import os
import yaml

configfile = yaml.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.yaml')), Loader=yaml.BaseLoader)

sleep = float(configfile['api_sleep'])

ws = websocket.WebSocket(sslopt={'cert_reqs': ssl.CERT_NONE})

#ws.connect(str(configfile['ws_api_base_url']) + '/realtime?subscribe=tradeBin1m:XBTUSD')
#ws.connect(str(configfile['ws_api_base_url']) + '/realtime?subscribe=tradeBin1m:XBTUSD,tradeBin5m:XBTUSD,trade:XBTUSD')

# OPEN INTEREST UPDATES
# ws.connect(str(configfile['ws_api_base_url']) + '/realtime?subscribe=instrument:XBTUSD')
# count = 0
# #start = time.time()
# while count < 5:
# 	res = ws.recv()
# 	res = json.loads(res)
# 	if 'table' in res.keys() and res['table'] == 'instrument' and res['action'] == 'partial':
# 		print(res['data'][0]['openInterest'])
# 		count += 1
# 	if 'table' in res.keys() and res['table'] == 'instrument' and res['action'] == 'update':
# 		for update in res['data']:
# 			if 'openInterest' in update.keys():
# 				print(update['openInterest'])
# 				#print(time.time() - start)
# 				#start = time.time()
# 				count += 1

# FUNDING RATE
# ws.connect(str(configfile['ws_api_base_url']) + '/realtime?subscribe=instrument:XBTUSD')
# count = 0
# #start = time.time()
# while count < 5:
# 	res = ws.recv()
# 	res = json.loads(res)
# 	if 'table' in res.keys() and res['table'] == 'instrument' and res['action'] == 'partial':
# 		print(res['data'][0]['fundingRate'])
# 		count += 1
# 	if 'table' in res.keys() and res['table'] == 'instrument' and res['action'] == 'update':
# 		for update in res['data']:
# 			if 'fundingRate' in update.keys():
# 				print(update['fundingRate'])
# 				#print(time.time() - start)
# 				#start = time.time()
# 				count += 1

# INDICATIVE FUNDING RATE
# ws.connect(str(configfile['ws_api_base_url']) + '/realtime?subscribe=instrument:XBTUSD')
# count = 0
# #start = time.time()
# while count < 5:
# 	res = ws.recv()
# 	res = json.loads(res)
# 	if 'table' in res.keys() and res['table'] == 'instrument' and res['action'] == 'partial':
# 		print(res['data'][0]['indicativeFundingRate'])
# 		count += 1
# 	if 'table' in res.keys() and res['table'] == 'instrument' and res['action'] == 'update':
# 		for update in res['data']:
# 			if 'indicativeFundingRate' in update.keys():
# 				print(update['indicativeFundingRate'])
# 				#print(time.time() - start)
# 				#start = time.time()
# 				count += 1

# TRADE VOLUME 1m BUCKET
# ws.connect(str(configfile['ws_api_base_url']) + '/realtime?subscribe=tradeBin1m:XBTUSD')
# count = 0
# #start = time.time()
# while count < 5:
# 	res = ws.recv()
# 	res = json.loads(res)
# 	if 'table' in res.keys() and res['table'] == 'tradeBin1m' and res['action'] == 'partial':
# 		#print(res['data'][0]['timestamp'])
# 		print(res['data'][0]['volume'])
# 		count += 1
# 	if 'table' in res.keys() and res['table'] == 'tradeBin1m' and res['action'] == 'insert':
# 		for update in res['data']:
# 			if 'volume' in update.keys():
# 				#print(update['timestamp'])
# 				print(update['volume'])
# 				#print(time.time() - start)
# 				#start = time.time()
# 				count += 1

# count = 0
# old_volume_1m = 1
# old_volume_5m = 1
# while count < 50:
# 	result = ws.recv()
# 	result = json.loads(result)
# 	print(result)
# 	if 'action' in result.keys() and result['action'] == 'insert':
# 		if result['table'] == 'tradeBin1m':
# 			current_volume_1m = result['data'][0]['volume']
# 			volume_change_percent_1m = 100 * (current_volume_1m - old_volume_1m) / old_volume_1m
# 			old_volume_1m = result['data'][0]['volume']
# 			print(round(volume_change_percent_1m, 2))
# 		if result['table'] == 'tradeBin5m':
# 			current_volume_5m = result['data'][0]['volume']
# 			volume_change_percent_5m = 100 * (current_volume_5m - old_volume_5m) / old_volume_5m
# 			old_volume_5m = result['data'][0]['volume']
# 			print(round(volume_change_percent_5m, 2))
# 		print(count)
# 		print()
# 	#print(result)
# 	count += 1
# 	time.sleep(sleep)

# count = 0
# recent_trades = []
# while count < 50:
# 	result = ws.recv()
# 	result = json.loads(result)
# 	if 'table' in result.keys():
# 		if result['table'] == 'trade':
# 			for trade in result['data']:
# 				if len(recent_trades) < int(configfile['keep_trades']):
# 					recent_trades.append(trade['size'])
# 				else:
# 					recent_trades = recent_trades[1:]
# 					recent_trades.append(trade['size'])
# 					print(round(sum(recent_trades) / len(recent_trades), 2))
# 	count += 1

# open interest, current funding rate, and predicted funding rate
# response = requests.get(str(configfile['rest_api_base_url']) + '/instrument?symbol=' + str(configfile['symbol']) + '&count=1&reverse=false')
# print(response.json()[0]['openInterest'])
# print(response.json()[0]['fundingRate'])
# print(response.json()[0]['indicativeFundingRate'])
# time.sleep(sleep)

# funding rate history, last 100, not including the current funding rate
# response = requests.get(str(configfile['rest_api_base_url']) + '/funding?symbol=' + str(configfile['symbol']) + '&count=100&reverse=true')
# datetime_object = datetime.datetime.strptime(response.json()[0]['timestamp'], '%Y-%m-%d' + 'T' + '%H:%M:%S.%f' + 'Z')
# print(datetime_object + datetime.timedelta(hours=8))
# print(type(response.json()[0]['timestamp']))


