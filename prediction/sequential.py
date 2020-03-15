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

    bias = 0.00 # smaller the better
    for i in range(timeseries.raw_size() - 1, timeseries.raw_size() - observation_range, -1):
        if timeseries.raw_datapoint(timeseries.raw_size() - 1) < timeseries.raw_datapoint(i):
            bias += 1
        else:
            bias -= 1
    # always be negative (positive momentum * negative = negative bias)
    # (negative momentum * negative = positive bias)
    bias *= -votality_rate 
    return bias
def regression_momentum_bias(timeseries, observation_range):
    """ my own implementation of linear regression on a stock matrix to calculate its rate of growth """
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
    high_low_slope = (timeseries.raw_datapoint(high) - timeseries.raw_datapoint(low)) / (high - low)
    
    slope = (high_low_slope + end_point_slope) / 2
    
    line = [i * slope + end_point_bias for i in range(timeseries.raw_size())]
    #graph(timeseries.raw_matrix(), "green", "trend.png", False)
    #graph(line, "red", "trend.png", False)
    
    bias = 0
    for i in range(timeseries.raw_size() - 2, timeseries.raw_size() - 1 - observation_range, -1):
        if timeseries.raw_datapoint(i) < timeseries.raw_datapoint(timeseries.raw_size() - 1):
            bias += 1
    bias *= slope
    return bias

def sequential_prediction(model=None, stock_id=None, date=None, graphing=True, log=True, add_bias=True, itr=10):
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

    bias = 0.00
    if add_bias == True:
        bias_mode = int(input("Bias Type [0: Votality, 1: Regression] :: "))
        # compute bias using momentum calculations with VIX index
        if bias_mode == 1:
            bias = regression_momentum_bias(timeseries, WEEK)
        else:
            bias = vix_momentum_bias(timeseries, date, WEEK, MONTH)

    for count in range(itr):
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
                prediction += bias
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
    stock, prediction = sequential_prediction(itr=15, add_bias=False)

    print("\n\nEstimated Stock Matrix = ", prediction)
    print("Estimated Change: ", prediction[len(prediction) - 1] - stock[len(stock) - 1], "\n\n")

    git_update()
