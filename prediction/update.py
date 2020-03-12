#!/usr/bin/env python3

import os
import time
import model as model
import tqdm as tqdm
from service import all_models
from service import download_stock, partition_time_series, git_update
from financial import QUARTER, MONTH
from financial import STANDARD_SAMPLING_RANGE
from financial import sampling, moving_average
from datetime import date

os.system('clear')
print("Running ./update.py for updating all existing models...")
time.sleep(2)
os.system('clear')

models = all_models()

download_date = ""
today = str(date.today())
date_info = today.split("-")
date_info[0] = str(int(date_info[0]) - 1)
for i in range(len(date_info)):
    if i == len(date_info) - 1:
        download_date += date_info[i]
    else:
        download_date += date_info[i] + "-"

if __name__ == "__main__":
    print("UPDATING ALL EXISTING MODELS:\n")
    for m in models:
        stock, id = download_stock(m, download_date, 1, False)
        if len(stock) <= QUARTER:
            print("Failed! [NOT ENOUGH DATA]")
        else:
            dataset = partition_time_series(stock, QUARTER, 35, False)
            for timeseries in dataset:
                matrix = moving_average(timeseries, MONTH)
                matrix = sampling(matrix, 0, 2, STANDARD_SAMPLING_RANGE)
                timeseries.set_sampled_matrix(matrix)
                timeseries.normalize_timeseries()
            predictor = model.Model(m)
            predictor.update(dataset, True, 10, 32, 0)
            print("Updated model for {0}!". format(m))
    git_update()
            
