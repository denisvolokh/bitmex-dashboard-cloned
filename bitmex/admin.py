from django.contrib import admin

from bitmex.models import FundingRate, IndicativeFundingRate
from bitmex.models import PredictedFundingRate
from bitmex.models import Volume1m
from bitmex.models import Volume5m
from bitmex.models import Volume1h
from bitmex.models import Volume1d
from bitmex.models import Trade
from bitmex.models import Instrument
from bitmex.models import Parameter
from bitmex.models import Threshold
from bitmex.models import ThresholdAlert
from bitmex.models import Level

class ParameterAdmin(admin.ModelAdmin):
	list_display = [
		"key",
		'value',
	]

class LevelAdmin(admin.ModelAdmin):
	list_display = [
		"price_level",
		'type',
	]

class ThresholdAdmin(admin.ModelAdmin):
	list_display = [
		"timeframe",
		'threshold_type',
		"threshold_value_percent"
	]

class ThresholdAlertAdmin(admin.ModelAdmin):
	list_display = [
		"alert_type",
		'alert_message',
		"status",
		"created_at",
	]

class InstrumentAdmin(admin.ModelAdmin):
	list_display = [
		"symbol",
		'open_interest',
		'timestamp'
	]
	
class FundingRateAdmin(admin.ModelAdmin):
    list_display = [
    					'funding_timestamp',
    					'funding_rate',
    				]
				

class IndicativeFundingRateAdmin(admin.ModelAdmin):
    list_display = [
    					'timestamp',
    					'indicative_funding_rate',
    				]

class PredictedFundingRateAdmin(admin.ModelAdmin):
    list_display = [
    					'timestamp',
    					'predicted_funding_rate',
    				]

class Volume1mAdmin(admin.ModelAdmin):
	list_filter = (
		'symbol',
	)
	list_display = (
		"symbol",
		'timestamp',
		'volume1m',
	)

class Volume1hAdmin(admin.ModelAdmin):
	list_filter = (
		'symbol',
	)
	list_display = (
		"symbol",
		'timestamp',
		'volume1h',
	)

class Volume1dAdmin(admin.ModelAdmin):
	list_filter = (
		'symbol',
	)
	list_display = (
		"symbol",
		'timestamp',
		'volume1d',
	)

class TradeAdmin(admin.ModelAdmin):
	list_display = (
		'symbol',
		'side',
		'size',
		'price',
		"timestamp",
	)
	list_filter = ("symbol",)

class Volume5mAdmin(admin.ModelAdmin):
	list_filter = (
		'symbol',
	)
	list_display = (
		"symbol",
        'timestamp',
        'volume5m',
	)

admin.site.register(Level, LevelAdmin)
admin.site.register(ThresholdAlert, ThresholdAlertAdmin)
admin.site.register(Threshold, ThresholdAdmin)
admin.site.register(Parameter, ParameterAdmin)
admin.site.register(Instrument, InstrumentAdmin)
admin.site.register(Trade, TradeAdmin)
admin.site.register(FundingRate, FundingRateAdmin)
admin.site.register(IndicativeFundingRate, IndicativeFundingRateAdmin)
admin.site.register(PredictedFundingRate, PredictedFundingRateAdmin)
admin.site.register(Volume1m, Volume1mAdmin)
admin.site.register(Volume5m, Volume5mAdmin)
admin.site.register(Volume1h, Volume1hAdmin)
admin.site.register(Volume1d, Volume1dAdmin)