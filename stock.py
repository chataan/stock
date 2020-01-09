
import os
import time as time
import tqdm as tqdm
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np

YEAR=0
MONTH=1
DATE=2
OPEN=3
CLOSE=7

def upload(path, log=True):
    """ Upload datapoints of a stock """
    uploaded = []
    data = []
    file = open(path, "r")
    info = file.readlines()
    for x in info:
        data.append(x)
        data[len(data) - 1] = data[len(data) - 1].replace("-", ",")
    del data[0] # delete the line: "Date,Open,High,Low,Close,Adj Close,Volume" on the .csv file

    raw = []
    count = 0
    print("\nReading stock data from [", path, "]")
    if log == True:
        loop = tqdm.tqdm(total = len(data), position = 0, leave = False)
    for line in data:
        line = line.split(",")
        # convert all the numbers in the line as integers, create a StockDataPoint
        raw.append(float(line[OPEN]))
        raw.append(float(line[CLOSE]))
        count += 1
        if log == True:
            loop.set_description('Reading stock data...' .format(len(data)))
            loop.update(1)
            time.sleep(0.001)
        else:
            pass
    print("\n\nUploaded stock data successfully!")
    return raw