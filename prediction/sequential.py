#!/usr/bin/env python3

import os
from service import graph, select_model, download_stock
from service import fetch_last_time_series, git_update
from financial import rescale, moving_average, sampling
from financial import QUARTER, MONTH, WEEK, STANDARD_SAMPLING_RANGE
from financial import TimeSeries
from model import Model

def vix_momentum_bias(timeseries, date, votality_calculation_range, observation_range):
    vix, vix_id = download_stock("^vix", date, 1, False)
    for i in range(len(vix) - 1 - votality_calculation_range, 0, -1):
        del vix[i]
    votality_rate = (vix[len(vix) - 1] - vix[0]) / len(vix)

    bias_momentum = 0.00 # smaller the better
    for i in range(timeseries.raw_size() - 1, timeseries.raw_size() - observation_range, -1):
        if timeseries.raw_datapoint(timeseries.raw_size() - 1) < timeseries.raw_datapoint(i):
            bias_momentum += 1
        else:
            bias_momentum -= 1
    # always be negative (positive momentum * negative = negative bias)
    # (negative momentum * negative = positive bias)
    bias_momentum *= -votality_rate 
    return bias_momentum
def regression_momentum_bias(timeseries, observation_range):
    """ my own implementation of linear regression on a stock matrix """
    """ this is crappy. don't take this seriously """
    # set initial slope and bias based on the end points of the matrix
    timeseries.raw_datapoint(timeseries.raw_size() - 1)
    end_point_slope = (timeseries.raw_datapoint(timeseries.raw_size() - 1) - timeseries.raw_datapoint(0)) / timeseries.raw_size()
    end_point_bias = end_point_slope + timeseries.raw_datapoint(0)

    high, low = 0, 0
    for i in range(timeseries.raw_size()):
        if timeseries.raw_datapoint(i) > timeseries.raw_datapoint(high):
            high = i
        if timeseries.raw_datapoint(i) < timeseries.raw_datapoint(low):
            low = i
    
    print((timeseries.raw_datapoint(high) - timeseries.raw_datapoint(low)) / (high - low))

    line = [i * end_point_slope + end_point_bias for i in range(timeseries.raw_size())]

    graph(timeseries.raw_matrix(), "green", "trend.png", False)
    graph(line, "red", "trend.png", False)
    
    bias_momentum = 0.00
    return bias_momentum

def sequential_prediction(model=None, stock_id=None, date=None, graphing=True, log=True):
    if model == None:
        model = select_model()
        print("Model = [", model, "]\n")

    stock = None
    if stock_id == None or date == None:
        stock, id = download_stock()
    else:
        stock, id = download_stock(stock_id, date, 1, True)

    predictor = Model(model)
    timeseries, final_close = fetch_last_time_series(stock, QUARTER)
    prediction_matrix = []

    bias = int(input("Bias Type [0: Votality, 1: Regression] :: "))
    bias_momentum = 0.00
    # compute bias using momentum calculations with VIX index
    if bias == 1:
        bias_momentum = regression_momentum_bias(timeseries, WEEK)
    else:
        bias_momentum = vix_momentum_bias(timeseries, date, WEEK, MONTH)
    print(bias_momentum)

    for count in range(5):
        trend = moving_average(timeseries, MONTH)
        matrix = sampling(trend, 0, 2, STANDARD_SAMPLING_RANGE)
        timeseries.set_sampled_matrix(matrix)
        timeseries.normalize_timeseries()

        prediction = 0.00
        result = predictor.predict(timeseries)
        for i in range(result.shape[0]):
            for j in range(result.shape[1]):
                prediction = rescale(result[i][j], timeseries.minimum(), timeseries.maximum())
                # apply the pre-calculated bias to the prediction results
                prediction += bias_momentum
        prediction_matrix.append(prediction)
        raw = timeseries.raw_matrix()
        for i in range(0, len(raw)):
            raw[i] = rescale(raw[i], timeseries.minimum(), timeseries.maximum())
        del raw[0]
        raw.append(prediction)
        timeseries.set_raw_matrix(raw)
        count += 1

    if graphing == True:
        graph_title = "../Images/" + model + "_sequential_prediction_demo.png"
        graph(prediction_matrix, 'red', graph_title, False)
    return stock, prediction_matrix

if __name__ == "__main__":
    os.system('clear')
    stock, prediction = sequential_prediction()
    print("\n", prediction, "\n")
    git_update()
