#!/usr/bin/env python3

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import tqdm as tqdm
from stock import upload
from financial import MONTH, QUARTER, YEAR
from financial import MINIMUM_SAMPLING_RANGE, DEFAULT_SAMPLING_RANGE, MAXIMUM_SAMPLING_RANGE
from financial import partition_time_series
from financial import rolling_mean_trend
from financial import reduction
import matplotlib.pyplot as plt
import model as model

aapl = "Database/AAPL.csv" # Applc Inc.
goog = "Database/GOOG.csv" # Google Inc.
msft = "Database/MSFT.csv" # Microsoft Inc.
nvda = "Database/NVDA.csv" # NVIDIA Inc.
tsla = "Database/TSLA.csv" # Tesla Inc.

# search given stock query on Google Search Engine 
#query += " finance.yahoo"
#search_result = None
#for link in googlesearch.search(query, tld="co.in", num=1, stop=1, pause=2):
    #search_result = str(link)
# acquire the past year worth of stock data

long_term_processor = None
short_term_processor = None

if __name__ == "__main__":
    os.system('clear')
    google = upload(goog, True)
    dataset = partition_time_series(google, YEAR)

    # compute trend line of each time series
    loop = tqdm.tqdm(total = len(dataset), position = 0, leave = False)
    for timeseries in dataset:
        loop.set_description('Analyzing time series trend line and spike analysis ' .format(len(dataset)))
        trendline, prediction = rolling_mean_trend(timeseries, QUARTER)
        timeseries.set_trendline_matrix(trendline)
        timeseries.set_trendline_matrix(reduction(timeseries))
        timeseries.append_trend_datapoint(prediction)
        loop.update(1)
    print("\nCompleted trend line analysis")
    loop.close()

    # create a Keras model
    model = model.KerasPredictor(dataset, "google")
    model.train() # this may take up to 2 ~ 8 hours depending on data dimensions