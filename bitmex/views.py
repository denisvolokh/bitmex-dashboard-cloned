from django.shortcuts import render
from django.http import JsonResponse

from bitmex.models import FundingRate
from bitmex.models import PredictedFundingRate, IndicativeFundingRate
from bitmex.models import Volume1m
from bitmex.models import Volume5m
from bitmex.models import Volume1h
from bitmex.models import Volume1d
from bitmex.models import Trade
from bitmex.models import Instrument
from bitmex.models import Parameter
from bitmex.models import Threshold
from bitmex.models import Level
from bitmex.serializers import ParameterSerializer, ThresholdSerializer

from django.views.decorators.csrf import csrf_exempt

import requests
import yaml
import os
import time
import datetime
import json
import websocket
import ssl
import os
import ccxt
import pandas as pd
from rest_framework import filters, status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from bitmex_data_loader import get_bitmex_data
from bitmex.utils import calc_levels

TIMEFRAMES = {
	'1m': 60*1000,
	'5m': 5*60*1000,
	'15m': 15*60*1000,
	'30m': 30*60*1000,
	'1h': 60*60*1000,
	'3h': 3*60*60*1000,
	"4h": 4*60*60*1000,
	'6h': 6*60*60*1000,
	'12h': 12*60*60*1000,
	'1d': 24*60*60*1000,
	'1w': 7*24*60*60*1000,
	'2w': 14*24*60*60*1000,
	'1M': None
}

def bitmex_dashboard(request):
	return render(request, 'bitmex_dashboard.html', context={})

class ParameterViewSet(viewsets.ModelViewSet):
    queryset = Parameter.objects.all()
    serializer_class = ParameterSerializer

class ThresholdViewSet(viewsets.ModelViewSet):
    queryset = Threshold.objects.all()
    serializer_class = ThresholdSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["timeframe", "threshold_type"]


class FundingAPIView(APIView):

	def get(self, request):
		
		try:
			current_funding_rate = FundingRate.objects \
				.latest("funding_timestamp")

		except FundingRate.DoesNotExist:
			pass

		try:
			past_current_funding = FundingRate.objects \
				.exclude(id=current_funding_rate.id) \
				.latest("funding_timestamp")

			past_current_funding_value = past_current_funding.funding_rate

			_rate_change = (current_funding_rate.funding_rate - past_current_funding_value) / abs(past_current_funding_value)
			_rate_change_bps = current_funding_rate.funding_rate * 10000 - past_current_funding_value * 10000

		except FundingRate.DoesNotExist:
			_rate_change = 0
			_rate_change_bps = 0

		sign = ""
		if _rate_change>=0:
			sign = "+"

		if _rate_change != 0:
			current_funding_rate_formatted = f"{round(current_funding_rate.funding_rate * 100, 4):.4f}% ({sign}{round(_rate_change * 100, 2)}%, {sign}{round(_rate_change_bps, 2)} bps)"
		else:
			current_funding_rate_formatted = f"{round(current_funding_rate.funding_rate * 100, 4):.4f}% (no change)" # ( - %, - bps)

		try:
			indicative_rate = IndicativeFundingRate.objects \
				.latest("timestamp")

		except IndicativeFundingRate.DoesNotExist:
			pass


		_rate_change = (indicative_rate.indicative_funding_rate - current_funding_rate.funding_rate) / abs(current_funding_rate.funding_rate)
		_rate_change_bps = indicative_rate.indicative_funding_rate * 10000 - current_funding_rate.funding_rate * 10000

		sign = ""
		if _rate_change>=0:
			sign = "+"

		if _rate_change != 0:
			predicted_funding_rate_formatted = f"{round(indicative_rate.indicative_funding_rate * 100, 4):.4f}% ({sign}{round(_rate_change * 100, 2)}%, {sign}{round(_rate_change_bps, 2)} bps)"
		else:
			predicted_funding_rate_formatted = f"{round(indicative_rate.indicative_funding_rate * 100, 4):.4f}% (no change)" # ( - %, - bps)
		

		result = {
			'current_funding_rate': current_funding_rate_formatted,
			'predicted_funding_rate': predicted_funding_rate_formatted,
			"next_funding_rate_change": str(current_funding_rate.funding_timestamp + datetime.timedelta(hours=8)) + ' UTC',
		}

		return Response(result)


class LevelsAPIView(APIView):

	def put(self, request):
		print(f"{request.data}")

		if "type" not in request.data:
			return Response({"error": "The type is missing"}, status=400)

		if "price_level" not in request.data:
			return Response({"error": "The price_level is missing"}, status=400)

		Level.objects.create(type=request.data.get("type"), price_level=request.data.get("price_level"))

		return Response("ok")

	def get(self, request):
		
		support_levels_dataset = Level.objects.filter(type="SUPPORT")
		resistance_levels_dataset = Level.objects.filter(type="RESISTANCE")
		custom_levels_dataset = Level.objects.filter(type="CUSTOM")

		result = {
			"support": [item.price_level for item in support_levels_dataset],
			"resistance": [item.price_level for item in resistance_levels_dataset],
			"custom": [item.price_level for item in custom_levels_dataset]
		}


		return Response(result)

	def delete(self, request):
		if "type" not in request.data:
			return Response({"error": "The type is missing"}, status=400)

		if "price_level" not in request.data:
			return Response({"error": "The price_level is missing"}, status=400)

		Level.objects.filter(type=request.data.get("type"), price_level=request.data.get("price_level")).delete()

		return Response("ok")

	def post(self, request):
		symbol_parameter = Parameter.objects.get(key="MARKET_DATA_SYMBOL")
		api_sleep_parameter = Parameter.objects.get(key="API_SLEEP")
		bitmex_public = ccxt.bitmex({})
		bitmex_time_now = bitmex_public.milliseconds()

		if "candles" not in request.data:
			return Response({"error": "Candles parameter is missing"}, status=400)

		candles = request.data.get("candles")

		if "timeframe" not in request.data:
			return Response({"error": "Timeframe parameter is missing"}, status=400)

		timeframe = request.data.get("timeframe")

		min_touches = int(request.data.get("minTouches", 1))
		stat_likeness_percent = int(request.data.get("likelinessPercent", 1.5))
		bounce_percent = int(request.data.get("bouncePercent", 5))

		print(f"Chart params. MinTouches: {min_touches}, stat_likeness_percent: {stat_likeness_percent}, bounce_percent: {bounce_percent}")

		params = {'partial': True}

		if timeframe in ['1m', '5m', '1h', '1d']:

			if candles > 500:
				runs = candles // 500
				remainder = candles % 500
				data_raw = []
				for i in reversed(range(runs + 1)):
					if i > 0:
						since = bitmex_time_now - (i * 500 * TIMEFRAMES[timeframe] + remainder * TIMEFRAMES[timeframe])
						bitmex_data = bitmex_public.fetch_ohlcv(
							symbol=symbol_parameter.value, 
							timeframe=timeframe, 
							limit=500, 
							since=since, 
							params=params
						)
						data_raw += bitmex_data
					time.sleep(api_sleep_parameter.value)

				if remainder > 0:
					since = bitmex_time_now - (remainder * TIMEFRAMES[timeframe])
					bitmex_data = bitmex_public.fetch_ohlcv(
						symbol=symbol_parameter.value, 
						timeframe=timeframe, 
						limit=remainder, 
						since=since, 
						params=params
					)
					data_raw += bitmex_data

			else:
				since = bitmex_time_now - candles * TIMEFRAMES[timeframe]
				data_raw = bitmex_public.fetch_ohlcv(
					symbol=symbol_parameter.value, 
					timeframe=timeframe, 
					limit=candles, 
					since=since, 
					params=params
				)
		
		else:
			data_raw = data_raw = get_bitmex_data(
				symbol_parameter.value, 
				timeframe, candles, 
				include_current_candle=True, 
				file_format=[], 
				api_cooldown_seconds=int(api_sleep_parameter.value)
			)

		data_raw = pd.DataFrame.from_records(data_raw)
		data_raw.columns = ['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume']

		data_json = data_raw.to_json(orient='records')

		support_levels, resistance_levels = calc_levels(
			candles=candles, 
			pd_data=data_raw,
			bounce_percent=bounce_percent,
			stat_likeness_percent=stat_likeness_percent,
			min_touches=min_touches
		)

		support_levels = [x for x in support_levels if x is not None]
		resistance_levels = [x for x in resistance_levels if x is not None]

		Level.objects.filter(type="SUPPORT").delete()
		Level.objects.filter(type="RESISTANCE").delete()

		print(f"Support Levels: {support_levels}")
		print(f"Resis Levels: {resistance_levels}")

		for level in support_levels:
			Level.objects.create(type="SUPPORT", price_level=float(level))
				
		for level in resistance_levels:
			Level.objects.create(type="RESISTANCE", price_level=float(level))
				
		custom_levels_dataset = Level.objects.filter(type="CUSTOM")

		return Response({
			"candles": json.loads(data_json),
			"support": support_levels,
			"resistance": resistance_levels,
			"custom": [item.price_level for item in custom_levels_dataset]
		})


def update_funding_rate():
	try:
		symbol = Parameter.objects.get(key="SYMBOL")
	
	except Parameter.DoesNotExist:
		return

	url = f"https://www.bitmex.com/api/v1/funding?symbol={symbol.value}&count=1&reverse=true" 

	print(f"[+] Request: {url}")

	response = requests.get(url)
	data = response.json()

	funding_data = data[0]
	print(f"[+] Funding Data: {funding_data}")

	funding_rate = funding_data['fundingRate']
	funding_rate_timestamp = funding_data['timestamp']

	print(f"[+] Funding Rate: {funding_rate} Funding Timestamp: {funding_rate_timestamp}")

	try:
		result = FundingRate.objects.update_or_create(
			funding_timestamp=funding_rate_timestamp,
			defaults={"funding_rate": funding_rate}
		)
	
	except Exception as e: 
		print(f"----------------> Funding Save Exception: {e}")


@csrf_exempt
def feeder(request):
	data = json.loads(request.body)

	if "table" not in data: 
		return JsonResponse({'result': "SUCCESS"})

	if data["table"] == "trade":
		for trade_item in data["data"]:
			Trade.objects.create(
				symbol=trade_item["symbol"], 
				side=trade_item["side"],
				size=trade_item["size"],
				price=trade_item["price"],
				timestamp=trade_item["timestamp"]
			)

	elif data["table"] == "tradeBin1m":
		for data_item in data["data"]:
			saved = Volume1m.objects.create(
				volume1m=data_item["volume"],
				timestamp=data_item["timestamp"],
				symbol=data_item["symbol"],
			)

	elif data["table"] == "tradeBin5m":
		for data_item in data["data"]:
			saved = Volume5m.objects.create(
				volume5m=data_item["volume"],
				timestamp=data_item["timestamp"],
				symbol=data_item["symbol"],
			)

	# elif data["table"] == "tradeBin1h":
	# 	for data_item in data["data"]:
	# 		saved = Volume1h.objects.create(
	# 			volume5m=data_item["volume"],
	# 			timestamp=data_item["timestamp"],
	# 			symbol=data_item["symbol"],
	# 		)
	
	# elif data["table"] == "tradeBin1d":
	# 	for data_item in data["data"]:
	# 		saved = Volume1d.objects.create(
	# 			volume5m=data_item["volume"],
	# 			timestamp=data_item["timestamp"],
	# 			symbol=data_item["symbol"],
	# 		)
	
	# elif data["table"] == "funding":
	# 	_data = data["data"]

	# 	try:
	# 		result = FundingRate.objects.update_or_create(
	# 			funding_timestamp=_data["timestamp"],
	# 			defaults={"funding_rate": _data["fundingRate"]}
	# 		)
		
	# 	except Exception as e: 
	# 		print(f"----------------> Funding Save Exception: {e}")

	elif data["table"] == "instrument":
		for data_item in data["data"]:
			if "openInterest" in data_item:
				saved = Instrument.objects.create(
					open_interest=data_item["openInterest"],
					timestamp=data_item["timestamp"],
					symbol=data_item["symbol"],
				)
			
			if "indicativeFundingRate" in data_item:
				# print(f"----------------> Indicative Funding Date: {data_item}")
				IndicativeFundingRate.objects.create(
					indicative_funding_rate=data_item["indicativeFundingRate"],
					timestamp=data_item["timestamp"]
				)

	return JsonResponse({'result': "SUCCESS"})
