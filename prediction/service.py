
import os
import time
import tqdm
from model import Model
import matplotlib.pyplot as plt
from stock import upload
from financial import rescale
from financial import WEEK, MONTH, QUARTER, YEAR
from financial import MINIMUM_SAMPLING_RANGE, STANDARD_SAMPLING_RANGE, MAXIMUM_SAMPLING_RANGE
from financial import TimeSeries, sampling, moving_average
from pandas_datareader.data import DataReader

YEAR=0
MONTH=1
DATE=2
OPEN=3
CLOSE=6

def git_update():
    os.system("git remote set-url origin git@github.com:junyoung-sim/stock")
    os.system("git add -A")
    os.system("git commit -am 'Automated Commision'")
    os.system("git push")
def graph(matrix, _color, save_name, show=False):
    count = []
    for i in range(len(matrix)):
        count.append(i)
    plt.plot(count, matrix, color=_color)
    plt.xlabel("Count")
    plt.ylabel("Value")
    if show != False:
        plt.show()
    plt.savefig(save_name)
def download_stock(stock_id="", start_date="", period=1, log=True):
    """ stock_id --> ex: AAPL (str)
        start_date --> ex: 2020-01-19 (str) """
    if (stock_id == "") & (start_date == ""):
        stock_id = input("Enter stock ID (ex: AAPL) = ")
        start_date = input("Enter start date (ex: 2020-01-19) = ")
    else:
        pass
    stock = DataReader(stock_id, "yahoo", start_date)
    csv = "../Database/" + stock_id + ".csv"
    stock.to_csv(csv)

    uploaded = []
    data = []
    file = open(csv, "r")
    info = file.readlines()
    for x in info:
        data.append(x)
        data[len(data) - 1] = data[len(data) - 1].replace("-", ",")
    del data[0] # delete the line: "Date,Open,High,Low,Close,Adj Close,Volume" on the .csv file

    raw = []
    count = 0
    print("\nReading stock data from [", csv, "]")
    if log == True:
        loop = tqdm.tqdm(total = int(len(data) / period), position = 0, leave = False)
    for i in range(0, len(data), period):
        line = data[i].split(",")
        raw.append(float(line[CLOSE]))
        count += 1
        if log == True:
            loop.set_description('Reading stock data...' .format(len(data)))
            loop.update(1)
            time.sleep(0.001)
        else:
            pass
    print("\n\nUploaded stock data successfully!")

    return raw, stock_id
def select_model():
    files = []
    for r, d, f in os.walk("Models"):
        for file in f:
            if '.h5' in file:
                file = str(file)
                file = file[:-9]
                files.append(file)
    select = -1
    while (select < 0) or (select > len(files)):
        print("\nSelect a model number:\n")
        for i in range(len(files)):
            print("     [{0}]:   {1}" .format(i, files[i]))
    
        print("\n")
        select = int(input(": "))

        if (select < 0) or (select > len(files)):
            print("\nPlease select a model number listed above!\n")
            time.sleep(2)
            os.system("clear")
    print("\n", files[select], "model selected!!")
    return files[select]

def fetch_last_time_series(stock, timeseries_split_range):
    raw = []
    for i in range(len(stock) - timeseries_split_range, len(stock)):
        raw.append(stock[i])
    return TimeSeries(raw), stock[len(stock) - 1]
def partition_time_series(stock, timeseries_split_range, ignore_percentage=35):
    dataset = []
    # discard 35% (default) of the stock datapoint (since too old datapoints = obsolete)
    ignore_breakpoint = int((len(dataset) * ignore_percentage) / 100)
    for sets in range(ignore_breakpoint, (len(stock) - timeseries_split_range + 1)):
        raw = []
        for i in range(sets, (sets + timeseries_split_range)):
            raw.append(stock[i])
        dataset.append(TimeSeries(raw))
        raw = []

    # set breakpoints to split the dataset into three categories: training, validating
    training_dataset_breakpoint = int((len(dataset) * 80) / 100)
    validation_dataset_breakpoint = training_dataset_breakpoint + int((len(dataset) * 20) / 100)

    amount_of_training_datasets = 0
    amount_of_validation_datasets = 0
    for i in range(len(dataset)):
        if i <= training_dataset_breakpoint:
            dataset[i].set_dataset_label("TRAINING")
            amount_of_training_datasets += 1
        else:
            dataset[i].set_dataset_label("VALIDATING")
            amount_of_validation_datasets += 1
    print("Completed stock time series partitioning! [Training = {0}, Validation = {1}]" .format(amount_of_training_datasets, amount_of_validation_datasets))
    print("Each time series data contains a total of {0} datapoints!\n" .format(dataset[0].raw_size()))
    return dataset
    