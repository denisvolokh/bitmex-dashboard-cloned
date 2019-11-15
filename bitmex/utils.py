from datetime import datetime

def calc_levels(candles, pd_data, min_touches=1, stat_likeness_percent=1.5, bounce_percent=5):

    # S/R indicator windows
    support_resistance_window = 50
    support_resistance_window_overall = int(candles * 0.3)

    # number of supports / resistances to be plotted on chart
    n_levels = 15
    # number of candles to extend the S/R lines to the left
    extend_left = 10
    # number of candles to extend the S/R lines to the right
    extend_right = support_resistance_window + 20

    usd_support_distance = 10

    # get information about timespan of the backtest period
    ts_from = pd_data.loc[0, 'Timestamp']
    time_from = datetime.fromtimestamp(ts_from / 1000).strftime('%d.%m.%Y %H:%M:%S')

    ts_to = pd_data.loc[len(pd_data) - 1, 'Timestamp']
    time_to = datetime.fromtimestamp(ts_to / 1000).strftime('%d.%m.%Y %H:%M:%S')

    total_seconds = float((ts_to - ts_from) / 1000)
    day = total_seconds // (24 * 3600)
    total_seconds = total_seconds % (24 * 3600)
    hour = total_seconds // 3600
    total_seconds %= 3600
    minutes = total_seconds // 60
    total_seconds %= 60
    seconds = total_seconds

    # dicts where S/R levels were found with keys being the candle index of the S/R level and values being the price
    supports = list()
    resistances = list()
    # fill the above lists and dicts using the above defined function
    for i in range(0, len(pd_data) - (support_resistance_window + 1)):
        low = pd_data['Low'][i:i + support_resistance_window].reset_index()
        high = pd_data['High'][i:i + support_resistance_window].reset_index()
        sup, res = supres(low['Low'], high['High'], min_touches=min_touches, stat_likeness_percent=stat_likeness_percent, bounce_percent=bounce_percent)
        
        supports.append(sup)
        resistances.append(res)

    supports = list(set(supports))
    resistances = list(set(resistances))

    return supports, resistances


def supres(low, high, min_touches=1, stat_likeness_percent=1.5, bounce_percent=5):
    # Setting default values for support and resistance to None
    sup = None
    res = None
    # Identifying local high and local low
    maxima = high.max()
    minima = low.min()
    # Calculating distance between max and min (total price movement)
    move_range = maxima - minima
    # Calculating bounce distance and allowable margin of error for likeness
    move_allowance = move_range * (stat_likeness_percent / 100)
    bounce_distance = move_range * (bounce_percent / 100)
    # Test resistance by iterating through data to check for touches delimited by bounces
    touchdown = 0
    awaiting_bounce = False
    for x in range(0, len(high)):
        if abs(maxima - high[x]) < move_allowance and not awaiting_bounce:
            touchdown = touchdown + 1
            awaiting_bounce = True
        elif abs(maxima - high[x]) > bounce_distance:
            awaiting_bounce = False
    if touchdown >= min_touches:
        res = maxima
        # Test support by iterating through data to check for touches delimited by bounces
        touchdown = 0
        awaiting_bounce = False
    for x in range(0, len(low)):
        if abs(low[x] - minima) < move_allowance and not awaiting_bounce:
            touchdown = touchdown + 1
            awaiting_bounce = True
        elif abs(low[x] - minima) > bounce_distance:
            awaiting_bounce = False
    if touchdown >= min_touches:
        sup = minima

    return sup,res