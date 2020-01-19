#!/usr/bin/env python3

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import time
import model as model
import tqdm as tqdm
from stock import upload
from service import graph, download_stock
from financial import WEEK, MONTH, QUARTER, YEAR
from financial import MINIMUM_SAMPLING_RANGE, STANDARD_SAMPLING_RANGE, MAXIMUM_SAMPLING_RANGE
from financial import partition_time_series, sampling, rolling_mean_trend

os.system('clear')
print("Running ./train.py for generating/updating model")
time.sleep(2)
os.system('clear')

if __name__ == "__main__":
     # use service module to download stock from YAHOO
     # downloaded stock will be saved as "Database/stock.csv"
    id = download_stock()
    print("\nDownloaded ", id, " historical stock data [PATH=Database/stock.csv]")

    stock = upload("Database/stock.csv", True)
    dataset = partition_time_series(stock, QUARTER) # each time series will be a quarter-long (90 datapoints)

    # compute trend line of each time series
    loop = tqdm.tqdm(total = len(dataset), position = 0, leave = False)
    for timeseries in dataset:
        loop.set_description('Analyzing time series trend line and spike analysis ' .format(len(dataset)))
        matrix, prediction = rolling_mean_trend(timeseries, WEEK)
        matrix = sampling(matrix, 0, 2, STANDARD_SAMPLING_RANGE)
        timeseries.set_sampled_matrix(matrix)
        loop.update(1)
    print("\nCompleted trend line analysis")
    loop.close()

    # check if there is an existing model

    model = model.KerasTrainer(dataset, id.lower())
    model.train(True, 100, 32)