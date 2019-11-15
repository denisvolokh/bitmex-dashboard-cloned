from django.db import models

class Parameter(models.Model):
	key = models.CharField(max_length=150)
	value = models.CharField(max_length=150)

	def __str__(self):
		"""String for representing the Model object."""
		return f"{self.key} - {self.value}"

class Level(models.Model):
	type = models.CharField(max_length=50) # SUPPORT, RESISTANCE, CUSTOM
	price_level = models.DecimalField(max_digits=8, decimal_places=2, default=0)

class Threshold(models.Model):
	timeframe = models.CharField(max_length=25, default="", null=True, blank=True)
	threshold_type = models.CharField(max_length=50, default="")
	threshold_value_percent = models.DecimalField(max_digits=12, decimal_places=2, default=0)

class ThresholdAlert(models.Model):
	alert_type = models.CharField(max_length=50, default="") # VOLUME_CHANGE
	alert_message = models.CharField(max_length=255, default="")
	status = models.CharField(max_length=50, default="PENDING") # SKIP, SENT
	level = models.ForeignKey("Level", on_delete=models.CASCADE, null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True, editable=False)

class Instrument(models.Model):
	symbol = models.CharField(max_length=10)
	timestamp = models.DateTimeField(auto_now_add=True)
	open_interest = models.FloatField(null=True, blank=True)

	def __str__(self):
		"""String for representing the Model object."""
		return self.symbol

class FundingRate(models.Model):
	funding_timestamp = models.DateTimeField()
	funding_rate = models.FloatField(null=True, blank=True)

	# def __str__(self):
	# 	"""String for representing the Model object."""
	# 	return f"{self.funding_rate} {self.funding_timestamp}"

class IndicativeFundingRate(models.Model):
	timestamp = models.DateTimeField()
	indicative_funding_rate = models.FloatField(null=True, blank=True)

	def __str__(self):
		"""String for representing the Model object."""
		return f"{self.indicative_funding_rate} {self.timestamp}"

class PredictedFundingRate(models.Model):
	timestamp = models.DateTimeField(auto_now_add=True)
	predicted_funding_rate = models.FloatField(null=True, blank=True)

	def __str__(self):
		"""String for representing the Model object."""
		return self.predicted_funding_rate

class Volume1m(models.Model):
	"""Model persisting EOD cuts."""
	timestamp = models.DateTimeField(auto_now_add=True)
	volume1m = models.FloatField(null=True, blank=True)
	symbol = models.CharField(max_length=7, null=True, blank=True)

	def __str__(self):
		"""String for representing the Model object."""
		return str(self.volume1m)

class Volume5m(models.Model):
	"""Model persisting EOD cuts."""
	timestamp = models.DateTimeField(auto_now_add=True)
	volume5m = models.FloatField(null=True, blank=True)
	symbol = models.CharField(max_length=7, null=True, blank=True)

	def __str__(self):
		"""String for representing the Model object."""
		return str(self.volume5m)

class Volume1h(models.Model):
	"""Model persisting EOD cuts."""
	timestamp = models.DateTimeField(auto_now_add=True)
	volume1h = models.FloatField(null=True, blank=True)
	symbol = models.CharField(max_length=7, null=True, blank=True)

	def __str__(self):
		"""String for representing the Model object."""
		return str(self.volume1h)


class Volume1d(models.Model):
	"""Model persisting EOD cuts."""
	timestamp = models.DateTimeField(auto_now_add=True)
	volume1d = models.FloatField(null=True, blank=True)
	symbol = models.CharField(max_length=7, null=True, blank=True)

	def __str__(self):
		"""String for representing the Model object."""
		return str(self.volume1d)


class Trade(models.Model):
	"""
		Model persisting Trades.
	"""

	timestamp = models.DateTimeField()
	symbol = models.CharField(max_length=7)
	side = models.CharField(max_length=4)
	size = models.PositiveIntegerField(default=0)
	price = models.DecimalField(decimal_places=3, max_digits=9, default=0)

	def __str__(self):
		"""String for representing the Model object."""
		return f"{self.symbol} {self.side} {self.price} {self.size}"

	# {'table': 'trade', 'action': 'insert', 'data': [{'timestamp': '2019-09-13T02:01:41.746Z', 
	# 'symbol': 'XBTUSD', 'side': 'Buy', 'size': 50, 'price': 10365.5, 'tickDirection': 'PlusTick', 
	# 'trdMatchID': '608d7ac2-987e-a074-5446-544305153e1f', 'grossValue': 482350, 'homeNotional': 0.0048235, 'foreignNotional': 50}]}