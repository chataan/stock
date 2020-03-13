#!/usr/bin/env python3

import os
from service import graph, select_model, download_stock, fetch_last_time_series, git_update
from financial import rescale, moving_average, sampling, QUARTER, MONTH, WEEK, STANDARD_SAMPLING_RANGE
from financial import TimeSeries
from model import Model

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

    # compute bias using momentum calculations with VIX index
    vix, vix_id = download_stock("^vix", date, 1, True)
    for i in range(len(vix) - 1 - WEEK, 0, -1):
        del vix[i]
    votality_rate = (vix[len(vix) - 1] - vix[0]) / len(vix)

    bias_momentum = 0.00 # smaller the better
    for i in range(timeseries.raw_size() - 1, timeseries.raw_size() - 10, -1):
        if timeseries.raw_datapoint(i) < timeseries.raw_datapoint(i - 1):
            bias_momentum += 1
            print(bias_momentum * votality_rate)
            bias_momentum *= votality_rate
    bias_momentum *= -1.00

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
                # compare the distance of the last close price and the moving average trend line to add bias to the prediction
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
        for p in prediction_matrix:
            stock.append(p)
        graph_title = "../Images/" + model + "_sequential_prediction_demo.png"
        graph(stock, 'red', graph_title, False)
    return stock, prediction_matrix

if __name__ == "__main__":
    os.system('clear')
    stock, prediction = sequential_prediction()
    print("\n", prediction, "\n")
    git_update()
