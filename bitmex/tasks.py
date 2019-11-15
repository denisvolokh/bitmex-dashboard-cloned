from bitmex.models import Parameter, FundingRate, Volume1d, Volume1h, Volume1m, Trade
import time
import requests
# from celery import task
from bitmex.apps import app
import logging

@app.task(name="bitmex.tasks.update_test")
def update_test():
    logging.info("================================")


@app.task(name="bitmex.tasks.update_funding_rate", autoretry_for=(Exception,), exponential_backoff=2, retry_kwargs={'max_retries': 5}, retry_jitter=False)
def update_funding_rate():
    logging.info("=============== Updating Funding Rate =================")

    try:
        symbol = Parameter.objects.get(key="SYMBOL")
    
    except Parameter.DoesNotExist:
        return

    url = f"https://www.bitmex.com/api/v1/funding?symbol={symbol.value}&count=1&reverse=true" 

    print(f"[+] Request: {url}")

    response = requests.get(url)

    if not response.ok:
        raise Exception(f'GET {url} returned unexpected response code: {response.status_code}')

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


@app.task(name="bitmex.tasks.update_1d_volume", autoretry_for=(Exception,), exponential_backoff=2, retry_kwargs={'max_retries': 5}, retry_jitter=False)
def update_1d_volume():
    logging.info("=============== Updating 1d volume =================")

    try:
        symbol = Parameter.objects.get(key="SYMBOL")
    
    except Parameter.DoesNotExist:
        return

    url = f"https://www.bitmex.com/api/v1/trade/bucketed?binSize=1d&partial=false&symbol={symbol.value}&count=2&reverse=true" 

    print(f"[+] Request: {url}")

    response = requests.get(url)
    
    if not response.ok:
        raise Exception(f'GET {url} returned unexpected response code: {response.status_code}')

    data = response.json()
    trade_data = data[0]
    print(f"[+] Trade Data: {trade_data}")

    volume = trade_data['volume']
    trade_data_timestamp = trade_data['timestamp']

    print(f"[+] 1d Volume: {volume} Timestamp: {trade_data_timestamp}")

    try:
        saved = Volume1d.objects.update_or_create(
            timestamp=trade_data_timestamp, symbol=symbol.value,
            defaults={"volume1d": volume}
        )
    
    except Exception as e: 
        print(f"----------------> Volume 1d Save Exception: {e}")


@app.task(name="bitmex.tasks.update_1h_volume", autoretry_for=(Exception,), exponential_backoff=2, retry_kwargs={'max_retries': 5}, retry_jitter=False)
def update_1h_volume():
    logging.info("=============== Updating 1h volume =================")

    try:
        symbol = Parameter.objects.get(key="SYMBOL")
    
    except Parameter.DoesNotExist:
        return

    url = f"https://www.bitmex.com/api/v1/trade/bucketed?binSize=1h&partial=false&symbol={symbol.value}&count=2&reverse=true" 

    print(f"[+] Request: {url}")

    response = requests.get(url)

    if not response.ok:
        raise Exception(f'GET {url} returned unexpected response code: {response.status_code}')

    data = response.json()
    trade_data = data[0]
    print(f"[+] Trade Data: {trade_data}")

    volume = trade_data['volume']
    trade_data_timestamp = trade_data['timestamp']

    print(f"[+] 1h Volume: {volume} Timestamp: {trade_data_timestamp}")

    try:
        saved = Volume1h.objects.update_or_create(
            timestamp=trade_data_timestamp, symbol=symbol.value,
            defaults={"volume1h": volume}
        )
    
    except Exception as e: 
        print(f"----------------> Volume 1h Save Exception: {e}")


@app.task(name="bitmex.tasks.update_trade")
def update_trade():
    logging.info("=============== Update Trade =================")

    try:
        symbol = Parameter.objects.get(key="SYMBOL")
    
    except Parameter.DoesNotExist:
        return

    try:
        number_trades_parameter = Parameter.objects.get(key="VOLUME_NUMBER_OF_TRADES")
    
    except Parameter.DoesNotExist:
        return

    Trade.objects.filter().delete()

    url = f"https://www.bitmex.com/api/v1/trade?symbol={symbol.value}&count={number_trades_parameter.value}&reverse=true" 

    print(f"[+] Request: {url}")

    response = requests.get(url)
    data = response.json()

    for item in data:
        try:
            saved = Trade.objects.create(
                timestamp=item["timestamp"], 
                symbol=symbol.value,
                side=item["side"], 
                price=item["price"], 
                size=item["size"]
            )
        
        except Exception as e: 
            print(f"----------------> Trade Save Exception: {e}")