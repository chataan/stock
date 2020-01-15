#!/usr/bin/env python3

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import tqdm as tqdm
from stock import upload
from financial import MONTH, QUARTER, YEAR
from financial import MINIMUM_SAMPLING_RANGE, STANDARD_SAMPLING_RANGE, MAXIMUM_SAMPLING_RANGE
from financial import partition_time_series, sampling, rolling_mean_trend
import model as model
import matplotlib.pyplot as plt

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
    dataset = partition_time_series(google, QUARTER) # each time series will be a quarter-long (90 datapoints)

    # compute trend line of each time series
    loop = tqdm.tqdm(total = len(dataset), position = 0, leave = False)
    for timeseries in dataset:
        loop.set_description('Analyzing time series trend line and spike analysis ' .format(len(dataset)))
        matrix, prediction = rolling_mean_trend(timeseries, MONTH)
        matrix = sampling(matrix, STANDARD_SAMPLING_RANGE)
        timeseries.set_sampled_matrix(matrix)
        loop.update(1)
    print("\nCompleted trend line analysis")
    loop.close()

    count = []
    for i in range(dataset[0].sampled_size()):
        count.append(i)
    plt.plot(count, dataset[0].sampled_matrix(), color='red')
    plt.xlabel("datapoint count")
    plt.ylabel("value")
    plt.title("sampled trend line")
    plt.savefig("sampled.png")

    model = model.KerasTrainer(dataset, "google")
    model.train(True, 100, 32)