
import os
import time
import tqdm
from model import Model
import matplotlib.pyplot as plt
from financial import rescale
from financial import WEEK, MONTH, QUARTER, YEAR
from financial import MINIMUM_SAMPLING_RANGE, STANDARD_SAMPLING_RANGE, MAXIMUM_SAMPLING_RANGE
from financial import fetch_last_time_series, partition_time_series, sampling, rolling_mean_trend
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
def download_stock():
    """ stock_id --> ex: AAPL (str)
        start_date --> ex: 2020-01-19 (str) """
    stock_id = input("Enter stock ID (ex: AAPL) = ")
    start_date = input("Enter start date (ex: 2020-01-19) = ")
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
def run(stock, model_name):
    test = fetch_last_time_series(stock, QUARTER)

    print("Running time series processing... ", end="")
    matrix, prediction = rolling_mean_trend(test, MONTH)
    matrix = sampling(matrix, 0, 2, STANDARD_SAMPLING_RANGE)
    test.set_sampled_matrix(matrix)
    print("DONE!\n")

    predictor = Model(model_name)
    result = predictor.predict(test)
    
    keras_prediction = 0.00
    for i in range(result.shape[0]):
        for j in range(result.shape[1]):
            keras_prediction = rescale(result[i][j], test.minimum(), test.maximum())
    return keras_prediction
def long_term_prediction(stock, _range, model_name):
    count = 0
    predictor = Model(model_name)
    timeseries = fetch_last_time_series(stock, QUARTER)
    prediction_matrix = []
    for val in timeseries.raw_matrix():
        prediction_matrix.append(rescale(val, timeseries.minimum(), timeseries.maximum()))
    
    matrix, prediction = rolling_mean_trend(timeseries, MONTH)
    matrix = sampling(matrix, 0, 2, STANDARD_SAMPLING_RANGE)
    timeseries.set_sampled_matrix(matrix)
    print(len(matrix))

    return prediction_matrix
def visualize_model_prediction(stock, model_name):
    dataset = partition_time_series(stock, QUARTER, 0)
    print("Processing time series dataset...\n")
    for timeseries in dataset:
        matrix, linear = rolling_mean_trend(timeseries, MONTH)
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