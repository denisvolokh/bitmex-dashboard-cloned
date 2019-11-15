from django.db.models.signals import post_save
from django.db.models import Sum
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .models import Trade, Volume1m, Volume5m, Instrument, Volume1h, Volume1d, Threshold, ThresholdAlert, FundingRate
from .models import Parameter, Level, IndicativeFundingRate
from bitmex.telegram_bot import telegram_bot_sendtext
from datetime import timedelta
from django.utils import timezone

import locale

locale.setlocale(locale.LC_ALL, '')
locale._override_localeconv = {'mon_thousands_sep': ' '}

@receiver(post_save, sender=FundingRate)
def post_save_funding_rate(sender, instance, **kwargs):
    saved_instance = FundingRate.objects.get(id=instance.id)

    try:
        past_funding_rate = FundingRate.objects \
            .exclude(id=instance.id) \
            .latest("funding_timestamp")

        past_rate = past_funding_rate.funding_rate

    except FundingRate.DoesNotExist:
        print(f"[+] Exception FundingRate: {saved_instance}")
        past_rate = 1

    _rate_change = (saved_instance.funding_rate - past_rate) / abs(past_rate)
    _rate_change_bps = instance.funding_rate * 10000 - past_rate * 10000

    sign = ""
    if _rate_change>=0:
        sign = "+"

    if _rate_change != 0:
        _formatted = f"{round(instance.funding_rate * 100, 4):.4f}% ({sign}{round(_rate_change * 100, 2)}%, {sign}{round(_rate_change_bps, 5)} bps)"
    else:
        _formatted = f"{round(instance.funding_rate * 100, 4):.4f}% (no change)" # ( - %, - bps)

    print(f"Current: {instance.funding_rate} Past: {past_rate}")
    print(f"Formatted: {_formatted}")

    async_to_sync(send_current_funding_rate)(message=_formatted, current_funding=saved_instance)


async def send_current_funding_rate(message: str, current_funding):
    next_funding_at = current_funding.funding_timestamp + timedelta(hours=8)

    group_name = f"instrument_XBTUSD"
    channel_layer = get_channel_layer()
    content = {
        "type": "instrument",
        "symbol": "XBTUSD",
        "current_funding_rate": message,
        'next_funding_rate_change': f'{next_funding_at} UTC',
    }

    await channel_layer.group_send(
        group_name,
        {
            # This "type" defines which handler on the Consumer gets
            # called.
            "type": "notify",
            "content": content
        }
    )


@receiver(post_save, sender=IndicativeFundingRate)
def post_save_indicative_funding_rate(sender, instance, **kwargs):
    print(f"[+] Post Save Indicative Funding Rate: {instance}")

    try:
        current_funding = FundingRate.objects \
            .latest("funding_timestamp")

        current_funding_rate = current_funding.funding_rate

    except FundingRate.DoesNotExist:
        current_funding_rate = 1

    _rate_change = (instance.indicative_funding_rate - current_funding_rate) / abs(current_funding_rate)
    _rate_change_bps = instance.indicative_funding_rate * 10000 - current_funding_rate * 10000

    sign = ""
    if _rate_change>=0:
        sign = "+"

    if _rate_change != 0:
        _formatted = f"{round(instance.indicative_funding_rate * 100, 4):.4f}% ({sign}{round(_rate_change * 100, 2)}%, {sign}{round(_rate_change_bps, 5)} bps)"
    else:
        _formatted = f"{round(instance.indicative_funding_rate * 100, 4):.4f}% (no change)" # ( - %, - bps)

    print(f"Current: {instance.indicative_funding_rate} Past: {current_funding_rate}")
    print(f"Formatted: {_formatted}")

    async_to_sync(send_predicted_funding_rate)(message=_formatted, current_funding_date=current_funding.funding_timestamp)


async def send_predicted_funding_rate(message: str, current_funding_date):
    group_name = f"instrument_XBTUSD"
    channel_layer = get_channel_layer()
    content = {
        "type": "instrument",
        "symbol": "XBTUSD",
        "predicted_funding_rate": message,
        'next_funding_rate_change': str(current_funding_date + timedelta(hours=8)) + ' UTC',
    }

    await channel_layer.group_send(
        group_name,
        {
            # This "type" defines which handler on the Consumer gets
            # called.
            "type": "notify",
            "content": content
        }
    )


@receiver(post_save, sender=Instrument)
def post_save_open_interest_threshold(sender, instance, **kwargs):
    print(f"[+] Post Save Open Interest Threshold: {instance}")

    try:
        open_interest_threshold = Threshold.objects.get(threshold_type="OPEN_INTEREST")
        threshold = float(open_interest_threshold.threshold_value_percent)

    except Threshold.DoesNotExist:
        print(f"[!!!] Threshold Open INterest is not found!")
        return

    if threshold == 0:
        return

    print(f"Threshold: {threshold}, Open Interest: {instance.open_interest}")
    parameter_sleep = Parameter.objects.get(key="OPEN_INTEREST_ALERT_SLEEP_SECONDS")

    try:
        existing_alert = ThresholdAlert.objects.filter(alert_type="OPEN_INTEREST_INCREASE").latest("created_at")

    except ThresholdAlert.DoesNotExist:
        existing_alert = None

    if instance.open_interest > threshold:
        parameter = Parameter.objects.get(key="OPEN_INTEREST_INCREASE_TEMPLATE")

        if existing_alert is None:
            ThresholdAlert.objects.create(
                alert_type="OPEN_INTEREST_INCREASE", 
                alert_message=parameter.value.format(round(instance.open_interest, 2))
            )
        
        if existing_alert:
            time_diff_seconds = (timezone.now() - existing_alert.created_at).total_seconds()

            if time_diff_seconds > int(parameter_sleep.value):
                ThresholdAlert.objects.create(
                    alert_type="OPEN_INTEREST_INCREASE", 
                    alert_message=parameter.value.format(round(instance.open_interest, 2))
                )


@receiver(post_save, sender=Instrument)
def post_save_instrument(sender, instance, **kwargs):
    # print(f"[+] Post Save Instrument: {instance}")

    try:
        latest_instrument = Instrument.objects \
            .filter(symbol=instance.symbol) \
            .exclude(id=instance.id) \
            .latest("timestamp")

        latest_instrument_open_interest = latest_instrument.open_interest

    except Instrument.DoesNotExist:
        latest_instrument_open_interest = 0

    async_to_sync(send_instrument)(instance.symbol, float(latest_instrument_open_interest))


async def send_instrument(symbol:str, open_interest: float):
    group_name = f"instrument_{symbol}"
    channel_layer = get_channel_layer()
    content = {
        "type": "instrument",
        "symbol": symbol,
        "open_interest": open_interest
    }

    await channel_layer.group_send(
        group_name,
        {
            # This "type" defines which handler on the Consumer gets
            # called.
            "type": "notify",
            "content": content
        }
    )


@receiver(post_save, sender=Volume5m)
def post_save_volume5m(sender, instance, **kwargs):
    # print(f"[+] Post Save Volume5m: {instance}")

    try:
        latest_volume5m = Volume5m.objects \
            .filter(symbol=instance.symbol) \
            .exclude(id=instance.id) \
            .latest("timestamp")

        latest_volume5m_volume = latest_volume5m.volume5m

    except Volume5m.DoesNotExist:
        latest_volume5m_volume = 1

    # calculate the 5m volume change in percent
    volume_change = instance.volume5m - latest_volume5m_volume
    volume_change_percent_5m = 100 * volume_change / latest_volume5m_volume

    async_to_sync(send_volume_updates)("5m", instance.symbol, float(volume_change), float(volume_change_percent_5m))


async def send_volume_updates(timeframe:str, symbol:str, volume_change: float,  volume_change_percent: float):
    print(f"[+] Send volume update to Web Socket!")
    print(f"[+] --> Timeframe: {timeframe}, Symbol: {symbol}, Volume Change: {volume_change}, Volume Change %: {volume_change_percent}")

    group_name = f"volume{timeframe}_{symbol}" # volume5m_XBTUSD
    channel_layer = get_channel_layer()

    content = {
        "type": f"volume{timeframe}",
        "symbol": symbol,
        f"volume{timeframe}_change_percent": '{0:+.2f}'.format(volume_change_percent),
        # f"volume{timeframe}_change": '{0:+}'.format(int(volume_change)),
        f"volume{timeframe}_change": "{:+,.0f}".format(int(volume_change)).replace(",", " ")
    }

    print(f"[+] --> Group Name: {group_name}, Socket Payload: {content}")

    await channel_layer.group_send(
        group_name,
        {
            "type": "notify",
            "content": content
        }
    )


@receiver(post_save, sender=Volume1m)
def post_save_volume1m(sender, instance, **kwargs):
    print(f"[!!!!!!!] Post Save Volume1m: {instance}")

    try:
        latest_volume1m = Volume1m.objects \
            .filter(symbol=instance.symbol) \
            .exclude(id=instance.id) \
            .latest("timestamp")

        latest_volume1m_volume = latest_volume1m.volume1m

    except Volume1m.DoesNotExist:
        latest_volume1m_volume = 1

    # calculate the 1m volume change in percent
    volume_change = instance.volume1m - latest_volume1m_volume
    volume_change_percent_1m = 100 * volume_change / latest_volume1m_volume

    # if volume_change < 0:
    #     volume_change = str(volume_change)
    #     volume_change_percent_1m = str(round(volume_change_percent_1m, 2))
    # else:
    #     volume_change = '+' + str(volume_change)
    #     volume_change_percent_1m = '+' + str(round(volume_change_percent_1m, 2))

    async_to_sync(send_volume_updates)("1m", instance.symbol, float(volume_change), float(volume_change_percent_1m))


@receiver(post_save, sender=Volume1h)
def post_save_volume1h(sender, instance, **kwargs):
    print(f"[+] ------> Post Save Volume1h: {instance.volume1h}")

    try:
        latest_volume1h = Volume1h.objects \
            .filter(symbol=instance.symbol) \
            .exclude(id=instance.id) \
            .latest("timestamp")

        latest_volume1h_volume = latest_volume1h.volume1h

    except Volume1h.DoesNotExist:
        latest_volume1h_volume = 1

    # calculate the 1m volume change in percent
    volume_change = instance.volume1h - latest_volume1h_volume
    volume_change_percent_1h = 100 * volume_change / latest_volume1h_volume

    async_to_sync(send_volume_updates)("1h", instance.symbol, float(volume_change), float(volume_change_percent_1h))


@receiver(post_save, sender=Volume1d)
def post_save_volume1d(sender, instance, **kwargs):
    # print(f"[+] Post Save Volume1d: {instance}")

    try:
        latest_volume1d = Volume1d.objects \
            .filter(symbol=instance.symbol) \
            .exclude(id=instance.id) \
            .latest("timestamp")

        latest_volume1d_volume = latest_volume1d.volume1d

    except Volume1d.DoesNotExist:
        latest_volume1d_volume = 1

    # calculate the 1d volume change in percent
    volume_change = instance.volume1d - latest_volume1d_volume
    volume_change_percent_1d = 100 * volume_change / latest_volume1d_volume

    async_to_sync(send_volume_updates)("1d", instance.symbol, float(volume_change), float(volume_change_percent_1d))


@receiver(post_save, sender=Trade)
def post_save_trade(sender, instance, **kwargs):
    # print(f"[+] Post Save Trade: {instance}")

    parameter_number_trades = Parameter.objects.get(key="VOLUME_NUMBER_OF_TRADES")
    number_trades = int(parameter_number_trades.value)

    if Trade.objects.filter().count() != number_trades:
        # print(f"[+] ---> Skip trades! Count: {Trade.objects.filter().count()}, Expecting: {number_trades}")
        return

    last_n_trades = Trade.objects.filter(symbol=instance.symbol).order_by("-timestamp")[:number_trades]
    trades_size_sum = last_n_trades.aggregate(Sum("size"))["size__sum"] # {'size__sum': 12135}

    keep_trades_ids = last_n_trades.values_list("id", flat=True)
    Trade.objects.filter().exclude(id__in=keep_trades_ids).delete()    

    async_to_sync(send_trade)(instance)
    async_to_sync(send_trade_volume)(instance.symbol, trades_size_sum)

async def send_trade_volume(symbol: str, trade_volume: int):
    group_name = f"trade_volume_{symbol}"
    channel_layer = get_channel_layer()
    content = {
        "type": f"trade_volume_{symbol}",
        "trade_volume": trade_volume
    }

    await channel_layer.group_send(
        group_name,
        {
            # This "type" defines which handler on the Consumer gets
            # called.
            "type": "notify",
            "content": content
        }
    )

async def send_trade(trade: Trade):
    group_name = trade.symbol
    channel_layer = get_channel_layer()
    content = {
        "type": "trade",
        "symbol": trade.symbol,
        "price": trade.price,
        "size": trade.size,
        "side": trade.side,
        # "timestamp": instance.timestamp
    }

    await channel_layer.group_send(
        group_name,
        {
            # This "type" defines which handler on the Consumer gets
            # called.
            "type": "notify",
            "content": content
        }
    )


@receiver(post_save, sender=Volume1m)
def post_save_volume1m_check_threshold(sender, instance, **kwargs):
    print(f"[+] Post Save Volume1m Check Threshold: {instance}")

    try:
        volume1m_threshold = Threshold.objects.get(timeframe="1m", threshold_type="VOLUME_CHANGE")
        threshold = float(volume1m_threshold.threshold_value_percent)

    except Threshold.DoesNotExist:
        print(f"[!!!] Threshold volume change 1m is not found!")
        return

    if threshold == 0:
        return

    # calculate the 1m volume change in percent
    try:
        latest_volume1m = Volume1m.objects \
            .filter(symbol=instance.symbol) \
            .exclude(id=instance.id) \
            .latest("timestamp")

        latest_volume1m_volume = latest_volume1m.volume1m

    except Volume1m.DoesNotExist:
        latest_volume1m_volume = 1

    # calculate the 1m volume change in percent
    volume_change = instance.volume1m - latest_volume1m_volume
    volume_change_percent_1m = abs(100 * volume_change / latest_volume1m_volume)

    print(f"Threshold: {threshold}, Volume Change 1m: {volume_change_percent_1m}")
    parameter_sleep = Parameter.objects.get(key="1M_VOLUME_INCREASE_ALERT_SLEEP_SECONDS")

    try:
        existing_1m_alert = ThresholdAlert.objects.filter(alert_type="1M_VOLUME_INCREASE").latest("created_at")

    except ThresholdAlert.DoesNotExist:
        existing_1m_alert = None

    if volume_change_percent_1m > threshold:
        parameter = Parameter.objects.get(key="1M_VOLUME_INCREASE_TEMPLATE")

        if existing_1m_alert is None:
            ThresholdAlert.objects.create(
                alert_type="1M_VOLUME_INCREASE", 
                alert_message=parameter.value.format(round(volume_change_percent_1m, 2))
            )
        
        if existing_1m_alert:
            time_diff_seconds = (timezone.now() - existing_1m_alert.created_at).total_seconds()
            # print(f"[+] Time Diff: {time_diff_seconds}, Parameter: {parameter_sleep.value}")

            if time_diff_seconds > int(parameter_sleep.value):
                ThresholdAlert.objects.create(
                    alert_type="1M_VOLUME_INCREASE", 
                    alert_message=parameter.value.format(round(volume_change_percent_1m, 2))
                )

@receiver(post_save, sender=Volume5m)
def post_save_volume5m_check_threshold(sender, instance, **kwargs):
    print(f"[+] Post Save Volume5m Check Threshold: {instance}")

    try:
        volume5m_threshold = Threshold.objects.get(timeframe="5m", threshold_type="VOLUME_CHANGE")
        threshold = float(volume5m_threshold.threshold_value_percent)

    except Threshold.DoesNotExist:
        print(f"[!!!] Threshold volume change 5m is not found!")
        return

    if threshold == 0:
        return

    # calculate the 5m volume change in percent
    try:
        latest_volume5m = Volume5m.objects \
            .filter(symbol=instance.symbol) \
            .exclude(id=instance.id) \
            .latest("timestamp")

        latest_volume5m_volume = latest_volume5m.volume5m

    except Volume5m.DoesNotExist:
        latest_volume5m_volume = 1

    # calculate the 5m volume change in percent
    volume_change = instance.volume5m - latest_volume5m_volume
    volume_change_percent_5m = abs(100 * volume_change / latest_volume5m_volume)

    print(f"Threshold: {threshold}, Volume Change 5m: {volume_change_percent_5m}")
    parameter_sleep = Parameter.objects.get(key="5M_VOLUME_INCREASE_ALERT_SLEEP_SECONDS")

    try:
        existing_5m_alert = ThresholdAlert.objects.filter(alert_type="5M_VOLUME_INCREASE").latest("created_at")

    except ThresholdAlert.DoesNotExist:
        existing_5m_alert = None

    if volume_change_percent_5m > threshold:
        parameter = Parameter.objects.get(key="5M_VOLUME_INCREASE_TEMPLATE")

        if existing_5m_alert is None:
            ThresholdAlert.objects.create(
                alert_type="5M_VOLUME_INCREASE", 
                alert_message=parameter.value.format(round(volume_change_percent_5m, 2))
            )
        
        if existing_5m_alert:
            time_diff_seconds = (timezone.now() - existing_5m_alert.created_at).total_seconds()
            # print(f"[+] Time Diff: {time_diff_seconds}, Parameter: {parameter_sleep.value}")

            if time_diff_seconds > int(parameter_sleep.value):
                ThresholdAlert.objects.create(
                    alert_type="5M_VOLUME_INCREASE", 
                    alert_message=parameter.value.format(round(volume_change_percent_5m, 2))
                )


@receiver(post_save, sender=Volume1h)
def post_save_volume1h_check_threshold(sender, instance, **kwargs):
    print(f"[+] Post Save Volume1h Check Threshold: {instance}")

    try:
        volume1h_threshold = Threshold.objects.get(timeframe="1h", threshold_type="VOLUME_CHANGE")
        threshold = float(volume1h_threshold.threshold_value_percent)

    except Threshold.DoesNotExist:
        print(f"[!!!] Threshold volume change 1h is not found!")
        return

    # calculate the 5m volume change in percent
    try:
        latest_volume1h = Volume1h.objects \
            .filter(symbol=instance.symbol) \
            .exclude(id=instance.id) \
            .latest("timestamp")

        latest_volume1h_volume = latest_volume1h.volume1h

    except Volume1h.DoesNotExist:
        latest_volume1h_volume = 1

    # calculate the 1h volume change in percent
    volume_change = instance.volume1h - latest_volume1h_volume
    volume_change_percent_1h = abs(100 * volume_change / latest_volume1h_volume)

    print(f"Threshold: {threshold}, Volume Change 1h: {volume_change_percent_1h}")
    parameter_sleep = Parameter.objects.get(key="1H_VOLUME_INCREASE_ALERT_SLEEP_SECONDS")

    try:
        existing_1h_alert = ThresholdAlert.objects.filter(alert_type="1H_VOLUME_INCREASE").latest("created_at")

    except ThresholdAlert.DoesNotExist:
        existing_1h_alert = None

    if volume_change_percent_1h > threshold:
        parameter = Parameter.objects.get(key="1H_VOLUME_INCREASE_TEMPLATE")

        if existing_1h_alert is None:
            ThresholdAlert.objects.create(
                alert_type="1H_VOLUME_INCREASE", 
                alert_message=parameter.value.format(round(volume_change_percent_1h, 2))
            )
        
        if existing_1h_alert:
            time_diff_seconds = (timezone.now() - existing_1h_alert.created_at).total_seconds()
            # print(f"[+] Time Diff: {time_diff_seconds}, Parameter: {parameter_sleep.value}")

            if time_diff_seconds > int(parameter_sleep.value):
                ThresholdAlert.objects.create(
                    alert_type="1H_VOLUME_INCREASE", 
                    alert_message=parameter.value.format(round(volume_change_percent_1h, 2))
                )


@receiver(post_save, sender=Volume1d)
def post_save_volume1d_check_threshold(sender, instance, **kwargs):
    print(f"[+] Post Save Volume1d Check Threshold: {instance}")

    try:
        volume1d_threshold = Threshold.objects.get(timeframe="1d", threshold_type="VOLUME_CHANGE")
        threshold = float(volume1d_threshold.threshold_value_percent)

    except Threshold.DoesNotExist:
        print(f"[!!!] Threshold volume change 1d is not found!")
        return

    if threshold == 0:
        return

    # calculate the 1d volume change in percent
    try:
        latest_volume1d = Volume1d.objects \
            .filter(symbol=instance.symbol) \
            .exclude(id=instance.id) \
            .latest("timestamp")

        latest_volume1d_volume = latest_volume1d.volume1h

    except Volume1d.DoesNotExist:
        latest_volume1d_volume = 1

    # calculate the 1d volume change in percent
    volume_change = instance.volume1d - latest_volume1d_volume
    volume_change_percent_1d = abs(100 * volume_change / latest_volume1d_volume)

    print(f"Threshold: {threshold}, Volume Change 1d: {volume_change_percent_1d}")
    parameter_sleep = Parameter.objects.get(key=f"SUPPORT_ALERT_SLEEP_SECONDS")

    try:
        existing_1d_alert = ThresholdAlert.objects.filter(alert_type="1D_VOLUME_INCREASE").latest("created_at")

    except ThresholdAlert.DoesNotExist:
        existing_1d_alert = None

    if volume_change_percent_1d > threshold:
        parameter = Parameter.objects.get(key="1D_VOLUME_INCREASE_TEMPLATE")

        if existing_1d_alert is None:
            ThresholdAlert.objects.create(
                alert_type="1D_VOLUME_INCREASE", 
                alert_message=parameter.value.format(round(volume_change_percent_1d, 2))
            )
        
        if existing_1d_alert:
            time_diff_seconds = (timezone.now() - existing_1d_alert.created_at).total_seconds()
            # print(f"[+] Time Diff: {time_diff_seconds}, Parameter: {parameter_sleep.value}")

            if time_diff_seconds > int(parameter_sleep.value):
                ThresholdAlert.objects.create(
                    alert_type="1D_VOLUME_INCREASE", 
                    alert_message=parameter.value.format(round(volume_change_percent_1d, 2))
                )

@receiver(post_save, sender=ThresholdAlert)
def post_save_threshold_alert(sender, instance, **kwargs):
    print(f"[+] Threshold Alert: {instance.alert_type}")

    telegram_bot_sendtext(instance.alert_message)

@receiver(post_save, sender=Trade)
def post_save_trade_check_levels_thresholds(sender, instance, **kwargs):
    current_price = instance.price

    try:
        threshold = Threshold.objects.get(threshold_type="SUPPORT")    
        support_threshold = threshold.threshold_value_percent

    except Threshold.DoesNotExist:
        support_threshold = 0

    try:
        threshold = Threshold.objects.get(threshold_type="RESISTANCE")    
        resistance_threshold = threshold.threshold_value_percent

    except Threshold.DoesNotExist:
        resistance_threshold = 0

    try:
        threshold = Threshold.objects.get(threshold_type="CUSTOM")    
        custom_threshold = threshold.threshold_value_percent

    except Threshold.DoesNotExist:
        custom_threshold = 0

    # support_levels = Level.objects.filter(type="SUPPORT").order_by("-price_level").values_list("price_level", flat=True)
    support_levels = Level.objects.filter(type="SUPPORT").order_by("-price_level")
    resistance_levels = Level.objects.filter(type="RESISTANCE").order_by("-price_level")
    # resistance_levels = Level.objects.filter(type="RESISTANCE").order_by("-price_level").values_list("price_level", flat=True)
    # custom_levels = Level.objects.filter(type="CUSTOM").order_by("-price_level").values_list("price_level", flat=True)
    custom_levels = Level.objects.filter(type="CUSTOM").order_by("-price_level")

    if support_threshold != 0:

        for support_level_item in support_levels:
            change_percent = (current_price - float(support_level_item.price_level)) / (current_price / 100)

            if change_percent != 0 and abs(change_percent) <= support_threshold:
                print(f"[+] Send Support Threshold Alert! Current Price: {instance.price}, Support Level: {support_level_item.price_level}, Target Threshold: {support_threshold}, Price change: {change_percent}")

                try:
                    existing_supprt_alert = ThresholdAlert.objects.filter(level=support_level_item).latest("created_at")

                except ThresholdAlert.DoesNotExist:
                    existing_supprt_alert = None

                parameter_template = Parameter.objects.get(key="SUPPORT_TEMPLATE")

                if existing_supprt_alert is None:
                    ThresholdAlert.objects.create(
                        level=support_level_item,
                        alert_type="SUPPORT", 
                        alert_message=parameter_template.value.format(abs(round(change_percent, 2)), support_level_item.price_level)
                    )
                    break

                if existing_supprt_alert:
                    parameter_sleep = Parameter.objects.get(key=f"SUPPORT_ALERT_SLEEP_SECONDS")
                    time_diff_seconds = (timezone.now() - existing_supprt_alert.created_at).total_seconds()
                    # print(f"[+] Time Diff: {time_diff_seconds}, Parameter: {parameter_sleep.value}")

                    if time_diff_seconds > int(parameter_sleep.value):
                        ThresholdAlert.objects.create(
                            level=support_level_item,
                            alert_type="SUPPORT", 
                            alert_message=parameter_template.value.format(abs(round(change_percent, 2)), support_level_item.price_level)
                        )
                        break       

    if resistance_threshold != 0:

        for resistance_level_item in resistance_levels:
            change_percent = (current_price - float(resistance_level_item.price_level)) / (current_price / 100)

            if change_percent != 0 and abs(change_percent) <= resistance_threshold:
                print(f"[+] Send Resistance Threshold Alert! Current Price: {instance.price}, Resistance Level: {resistance_level_item.price_level}, Target Threshold: {resistance_threshold}, Price change: {change_percent}")

                try:
                    existing_resis_alert = ThresholdAlert.objects.filter(level=resistance_level_item).latest("created_at")

                except ThresholdAlert.DoesNotExist:
                    existing_resis_alert = None

                parameter_template = Parameter.objects.get(key="RESISTANCE_TEMPLATE")

                if existing_resis_alert is None:
                    ThresholdAlert.objects.create(
                        level=resistance_level_item,
                        alert_type="SUPPORT", 
                        alert_message=parameter_template.value.format(abs(round(change_percent, 2)), resistance_level_item.price_level)
                    )
                    break

                if existing_resis_alert:
                    parameter_sleep = Parameter.objects.get(key=f"SUPPORT_ALERT_SLEEP_SECONDS")
                    time_diff_seconds = (timezone.now() - existing_resis_alert.created_at).total_seconds()
                    # print(f"[+] Time Diff: {time_diff_seconds}, Parameter: {parameter_sleep.value}")

                    if time_diff_seconds > int(parameter_sleep.value):
                        ThresholdAlert.objects.create(
                            level=resistance_level_item,
                            alert_type="RESISTANCE", 
                            alert_message=parameter_template.value.format(abs(round(change_percent, 2)), resistance_level_item.price_level)
                        )
                        break     

    if custom_threshold != 0:

        for custom_level_item in custom_levels:
            change_percent = (current_price - float(custom_level_item.price_level)) / (current_price / 100)

            if change_percent != 0 and abs(change_percent) <= custom_threshold:
                print(f"[+] Send Custom Threshold Alert! Current Price: {instance.price}, Custom Level: {custom_level_item.price_level}, Target Threshold: {custom_threshold}, Price change: {change_percent}")

                try:
                    existing_custom_alert = ThresholdAlert.objects.filter(level=custom_level_item).latest("created_at")

                except ThresholdAlert.DoesNotExist:
                    existing_custom_alert = None

                parameter_template = Parameter.objects.get(key="CUSTOM_TEMPLATE")

                if existing_custom_alert is None:
                    ThresholdAlert.objects.create(
                        level=custom_level_item,
                        alert_type="SUPPORT", 
                        alert_message=parameter_template.value.format(abs(round(change_percent, 2)), custom_level_item.price_level)
                    )
                    break

                if existing_custom_alert:
                    parameter_sleep = Parameter.objects.get(key=f"SUPPORT_ALERT_SLEEP_SECONDS")
                    time_diff_seconds = (timezone.now() - existing_custom_alert.created_at).total_seconds()
                    # print(f"[+] Time Diff: {time_diff_seconds}, Parameter: {parameter_sleep.value}")

                    if time_diff_seconds > int(parameter_sleep.value):
                        ThresholdAlert.objects.create(
                            level=custom_level_item,
                            alert_type="CUSTOM", 
                            alert_message=parameter_template.value.format(abs(round(change_percent, 2)), custom_level_item.price_level)
                        )
                        break     


    