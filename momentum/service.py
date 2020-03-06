
import os
import time
import tqdm
from model import Model
import matplotlib.pyplot as plt
from financial import rescale
from financial import WEEK, MONTH, QUARTER, YEAR
from financial import MINIMUM_SAMPLING_RANGE, STANDARD_SAMPLING_RANGE, MAXIMUM_SAMPLING_RANGE
from financial import TimeSeries, sampling, moving_average
from pandas_datareader import data

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
def download_stock(stock_id="", start_date=""):
    """ stock_id --> ex: AAPL (str)
        start_date --> ex: 2020-01-19 (str) """
    if (stock_id == "") & (start_date == ""):
        stock_id = input("Enter stock ID (ex: AAPL) = ")
        start_date = input("Enter start date (ex: 2020-01-19) = ")
    else:
        pass
    stock = data.DataReader(stock_id, "yahoo", start_date)
    csv = "Database/" + stock_id + ".csv"
    stock.to_csv(csv)
    return csv, stock_id
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

def visualize_model_prediction(stock, model_name):
    dataset = partition_time_series(stock, QUARTER, 0)
    print("Processing time series dataset...\n")
    for timeseries in dataset:
        matrix, linear = moving_average(timeseries, MONTH)
        matrix = sampling(matrix, 0, 2, STANDARD_SAMPLING_RANGE)
        timeseries.set_sampled_matrix(matrix)
    # create a matrix of predictions
    # graph the matrix with the actual stock price matrix
    prediction_matrix = []
    model = Model(model_name)
    description = "Computing model prediction on time series dataset..."
    loop = tqdm.tqdm(total = len(dataset), position = 0, leave = False)
    for timeseries in dataset:
        loop.set_description(description .format(len(dataset)))
        result = model.predict(timeseries)
        prediction = 0.00
        for i in range(result.shape[0]):
            for j in range(result.shape[1]):
                prediction = rescale(result[i][j], timeseries.minimum(), timeseries.maximum())
        prediction_matrix.append(prediction)
        loop.update(1)
    print("DONE!")
    loop.close()
    # graph the two matrices
    for i in range(0, len(stock) - len(prediction_matrix)):
        del stock[i]
    graph(stock, 'green', 'visualization', False)
    graph(prediction_matrix, 'red', 'visualization', False)