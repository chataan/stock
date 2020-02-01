#!/usr/bin/env python3

from stock import upload
from service import graph, download_stock
from financial import TimeSeries, QUARTER, rolling_mean_trend

csv, id = download_stock()
stock = upload(csv, True)
timeseries = TimeSeries(stock)

graph(timeseries.raw_matrix(), 'blue', 'apple', False)
trend, linear = rolling_mean_trend(timeseries, QUARTER)
graph(trend, 'red', 'apple_trend', False) 
