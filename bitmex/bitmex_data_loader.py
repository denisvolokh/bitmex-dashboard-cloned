# -*- coding: utf-8 -*-

import ccxt
import time
import csv
import pandas as pd

def get_bitmex_data(symbol, timeframe, length, include_current_candle = True, file_format = ['txt', 'csv'], api_cooldown_seconds = 0):

    """
    Download Crypto OHLCV Data from BitMEX.

    The function fetches OHLCV data via the specified paramteres from the public BitMEX API,
    merges it into a Pandas Data Frame and optionally saves the Data Frame as .txt and/or .csv file.
    Through concatenation more data than specified by the maximal request length of the exchange
    can be fetched.
    Additional timeframes are available (merged from smaller timeframes).

    Parameters
    ----------
    symbol : str
        Symbol of the underlying data, e.g. 'BTC/USD'

    timeframe : str
        Timeframe of the underlying data, e.g. '1h'

    length : int
        Number of Timeframes (Data length), e.g. 500

    include_current_candle : bool
        Include the current, not finished, candle, e.g. True

    file_format : str, list
        Which file format should be used to save the data, e.g. 'csv' or ['txt', 'csv']

    api_cooldown_seconds : int, float
        When fetching a lot of data this allows each request to the API to be made after
        the amount in seconds has passed.
        This prevents possible API errors due to too many requests within a short time.

    Returns
    -------
    Pandas Data Frame and optionally .txt and/or .csv file.
        A table with headers 'Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume' containing the requested data.

    Dependencies
    ------------
    import ccxt
    import time
    import csv
    import pandas as pd

    """

    data_limit = 500 # int(ccxt.bitmex({}).describe()['ratelimit']) returns 2000

    bitmex_symbols = [market['symbol'] for market in ccxt.bitmex({}).fetch_markets()]
    bitmex_timeframes = {'1m': 60*1000, '5m': 5*60*1000, '1h': 60*60*1000, '1d': 24*60*60*1000}
    missing_timeframes = {'3m': ['1m', 3, 1*60*1000], '15m': ['5m', 3, 5*60*1000], '30m': ['5m', 6, 5*60*1000], '2h': ['1h', 2, 60*60*1000], '3h': ['1h', 3, 60*60*1000], '4h': ['1h', 4, 60*60*1000], '6h': ['1h', 6, 60*60*1000], '12h': ['1h', 12, 60*60*1000], '3d': ['1d', 3, 24*60*60*1000], '1w': ['1d', 7, 24*60*60*1000], '2w': ['1d', 14, 24*60*60*1000]}

    timestamp = []
    openx = []
    high = []
    low = []
    close = []
    volume = []

    timestamp_temp = []
    openx_temp = []
    high_temp = []
    low_temp = []
    close_temp = []
    volume_temp = []

    proceed = True

    if symbol not in bitmex_symbols:
        print("ERROR:\tPlease use one of the following Symbols:\n\t" + "\n\t".join(sorted(bitmex_symbols)))
        proceed = False

    if not(timeframe in bitmex_timeframes.keys() or timeframe in missing_timeframes.keys()):
        print("ERROR:\tPlease use one of the following Timeframes:\n\tMinute:\t'1m', '3m', '5m', '15m', '30m',\n\tHour:\t'1h', '2h', '3h', '4h', '6h', '12h',\n\tDay:\t'1d', '3d',\n\tWeek:\t'1w', '2w'")
        proceed = False

    if not isinstance(length, int) or length < 1:
        print("ERROR:\tPlease use a reasonable number for the argument 'length'.")
        proceed = False

    if type(include_current_candle) != bool:
        print("ERROR:\tPlease use boolean values for argument 'include_current_candle' only.")
        proceed = False

    if not(file_format == 'txt' or file_format == 'csv' or file_format == ['txt'] or file_format == ['csv'] or file_format == ['csv', 'txt'] or file_format == ['txt', 'csv'] or
            file_format == '' or file_format == [] or file_format == [''] or file_format == None):
        print("ERROR:\tAllowed values for argument 'file_format' are 'csv', 'txt', ['csv', 'txt'].\n\tIf you do not wish to save the data please use either '', [''], [], None.")
        proceed = False

    if file_format == '' or file_format == [] or file_format == [''] or file_format == None:
        file_format = []

    if file_format == 'csv':
        file_format = ['csv']
    if file_format == 'txt':
        file_format = ['txt']

    if not isinstance(api_cooldown_seconds, (int, float)) or api_cooldown_seconds < 0 or api_cooldown_seconds > 60:
        print("ERROR:\tPlease use a reasonable 'api_cooldown_seconds' number of seconds (between 0 and 60).")
        proceed = False

    if proceed == True:
        if timeframe in missing_timeframes.keys():
            if include_current_candle == True:
                n_bulk = (length * missing_timeframes[timeframe][1]) // data_limit
                remainder = (length * missing_timeframes[timeframe][1]) % data_limit
            if include_current_candle == False:
                n_bulk = ((length + 1) * missing_timeframes[timeframe][1]) // data_limit
                remainder = ((length + 1) * missing_timeframes[timeframe][1]) % data_limit

            while n_bulk > 0:
                since = round(ccxt.bitmex({}).milliseconds() - (ccxt.bitmex({}).milliseconds() % (missing_timeframes[timeframe][1] * missing_timeframes[timeframe][2])) - (n_bulk * data_limit * missing_timeframes[timeframe][2]) - (remainder * missing_timeframes[timeframe][2]))
                for block in ccxt.bitmex({}).fetch_ohlcv(symbol = symbol, timeframe = missing_timeframes[timeframe][0], since = (since + (missing_timeframes[timeframe][1] * missing_timeframes[timeframe][2])), limit = data_limit):
                    timestamp_temp.append(block[0] - missing_timeframes[timeframe][2])
                    openx_temp.append(block[1])
                    high_temp.append(block[2])
                    low_temp.append(block[3])
                    close_temp.append(block[4])
                    volume_temp.append(block[5])
                n_bulk -= 1
                if n_bulk > 0 or remainder > 0:
                    time.sleep(api_cooldown_seconds)

            if remainder > 0:
                since = round(ccxt.bitmex({}).milliseconds() - (ccxt.bitmex({}).milliseconds() % (missing_timeframes[timeframe][1] * missing_timeframes[timeframe][2])) - (remainder * missing_timeframes[timeframe][2]))
                for block in ccxt.bitmex({}).fetch_ohlcv(symbol = symbol, timeframe = missing_timeframes[timeframe][0], since = (since + (missing_timeframes[timeframe][1] * missing_timeframes[timeframe][2])), limit = remainder + 1):
                    timestamp_temp.append(block[0] - missing_timeframes[timeframe][2])
                    openx_temp.append(block[1])
                    high_temp.append(block[2])
                    low_temp.append(block[3])
                    close_temp.append(block[4])
                    volume_temp.append(block[5])

            if length > 1:
                for i in [num for num in range(1, len(timestamp_temp), missing_timeframes[timeframe][1])][:-1]:
                    timestamp.append(timestamp_temp[i])
                    openx.append(openx_temp[i])
                    high.append(max(high_temp[i:i + missing_timeframes[timeframe][1]]))
                    low.append(min(low_temp[i:i + missing_timeframes[timeframe][1]]))
                    close.append(close_temp[i + (missing_timeframes[timeframe][1] - 1)])
                    volume.append(sum(volume_temp[i:i + missing_timeframes[timeframe][1]]))

                # append all available remaining smaller timeframes to the lists
                timestamp.append(timestamp_temp[i + missing_timeframes[timeframe][1]])
                openx.append(openx_temp[i + missing_timeframes[timeframe][1]])
                high.append(max(high_temp[i + missing_timeframes[timeframe][1]:]))
                low.append(min(low_temp[i + missing_timeframes[timeframe][1]:]))
                close.append(close_temp[-1])
                volume.append(sum(volume_temp[i + missing_timeframes[timeframe][1]:]))

            if length == 1:
                timestamp.append(timestamp_temp[1])
                openx.append(openx_temp[1])
                high.append(max(high_temp[1:]))
                low.append(min(low_temp[1:]))
                close.append(close_temp[-1])
                volume.append(sum(volume_temp[1:]))
            
        if timeframe not in missing_timeframes.keys():
            if include_current_candle == True:
                n_bulk = length // data_limit
                remainder = length % data_limit
            if include_current_candle == False:
                n_bulk = (length + 1) // data_limit
                remainder = (length + 1) % data_limit

            while n_bulk > 0:
                since = ccxt.bitmex({}).milliseconds() - (n_bulk * data_limit * bitmex_timeframes[timeframe]) - (remainder * bitmex_timeframes[timeframe])
                for block in ccxt.bitmex({}).fetch_ohlcv(symbol = symbol, timeframe = timeframe, since = (since + bitmex_timeframes[timeframe]), limit = data_limit):
                    timestamp.append(block[0] - bitmex_timeframes[timeframe])
                    openx.append(block[1])
                    high.append(block[2])
                    low.append(block[3])
                    close.append(block[4])
                    volume.append(block[5])
                n_bulk -= 1
                if n_bulk > 0 or remainder > 0:
                    time.sleep(api_cooldown_seconds)

            if remainder > 0:
                since = ccxt.bitmex({}).milliseconds() - (remainder * bitmex_timeframes[timeframe])
                for block in ccxt.bitmex({}).fetch_ohlcv(symbol = symbol, timeframe = timeframe, since = (since + bitmex_timeframes[timeframe]), limit = remainder + 1):
                    timestamp.append(block[0] - bitmex_timeframes[timeframe])
                    openx.append(block[1])
                    high.append(block[2])
                    low.append(block[3])
                    close.append(block[4])
                    volume.append(block[5])

        data_identifier = 'bitmex_' + ''.join(symbol.split('/')) + '_' + str(timeframe) + '_' + str(length) + ('_including_current_candle' if include_current_candle == True else '_NOT_including_current_candle')

        if file_format != []:
            for ending in file_format:
                # specify where to save the files e.g.
                #with open('/Users/username/Desktop/' + data_identifier + '.' + str(ending), 'w') as csvfile:
                with open(data_identifier + '.' + str(ending), 'w') as csvfile:
                    writer = csv.writer(csvfile, delimiter = ',', quotechar = '|', quoting = csv.QUOTE_MINIMAL)
                    writer.writerow([head for head in ['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume']])
                    if include_current_candle == True:
                        write = zip(timestamp, openx, high, low, close, volume)
                    if include_current_candle == False:
                        write = zip(timestamp[:-1], openx[:-1], high[:-1], low[:-1], close[:-1], volume[:-1])
                    for entry in write:
                        writer.writerow(entry)

        if include_current_candle == True:
            df = pd.DataFrame(list(zip(timestamp, openx, high, low, close, volume)), columns = ['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
            df.name = data_identifier
            return df
        if include_current_candle == False:
            df = pd.DataFrame(list(zip(timestamp[:-1], openx[:-1], high[:-1], low[:-1], close[:-1], volume[:-1])), columns = ['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
            df.name = data_identifier
            return df