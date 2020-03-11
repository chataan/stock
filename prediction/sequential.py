#!/usr/bin/env python3

import os
from stock import upload
from service import graph, select_model, download_stock, fetch_last_time_series, git_update
from financial import rescale, moving_average, sampling, QUARTER, MONTH, STANDARD_SAMPLING_RANGE
from model import Model

def sequential_prediction(model=None, stock_id=None, date=None, graphing=True, log=True):
    if model == None:
        model = select_model()
        print("Model = [", model, "]\n")

    if stock_id == None or date == None:
        path, id, date = download_stock()
    else:
        path, id, date = download_stock(stock_id, date)
    st = upload(path, 1, log)

    predictor = Model(model, "PREDICTION_MODEL")
    timeseries, final_close = fetch_last_time_series(st, QUARTER)
    prediction_matrix = []

    # compute bias using momentum calculations with VIX index
    path, id, date = download_stock("^vix", date)
    vix = upload(path, 1, log)
    vix_average = 0.00
    vix_timeseries, last_vix = fetch_last_time_series(vix, 10)
    for i in range(vix_timeseries.raw_size()):
        vix_average += vix_timeseries.raw_datapoint(i)
    vix_average /= vix_timeseries.raw_size()
    print(vix_average)

    bias_momentum = 0.00 # smaller the better
    for i in range(timeseries.raw_size() - 1, timeseries.raw_size() - 10, -1):
        if timeseries.raw_datapoint(timeseries.raw_size() - 1) < timeseries.raw_datapoint(i):
            bias_momentum += 1
    bias_momentum *= vix_average / 5
    #print("\nBIAS = [", bias_momentum, "]\n")

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
                prediction -= bias_momentum
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
    return prediction_matrix

if __name__ == "__main__":
    os.system('clear')
    prediction = sequential_prediction()
    print(prediction)
    git_update()
