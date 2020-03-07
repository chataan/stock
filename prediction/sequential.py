#!/usr/bin/env python3

import os
from stock import upload
from service import graph, select_model, download_stock, fetch_last_time_series, git_update
from financial import rescale, moving_average, sampling, QUARTER, MONTH, STANDARD_SAMPLING_RANGE
from model import Model

if __name__ == "__main__":
    os.system('clear')
    model = select_model()
    print("Model = [", model, "]\n")

    path, id, date = download_stock()
    st = upload(path, 1, True)

    predictor = Model(model, "PREDICTION_MODEL")
    timeseries, final_close = fetch_last_time_series(st, QUARTER)
    prediction_matrix = []

    path, id, date = download_stock("^vix", date)
    vix = upload(path, 1, False)
        
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
            bias_momentum *= vix_average / 100
    

    for count in range(3):
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
                prediction -= (vix_average * bias_momentum)
        prediction_matrix.append(prediction)
        raw = timeseries.raw_matrix()
        for i in range(0, len(raw)):
            raw[i] = rescale(raw[i], timeseries.minimum(), timeseries.maximum())
        del raw[0]
        raw.append(prediction)
        timeseries.set_raw_matrix(raw)
        count += 1
        if count % 10 == 0:
            print("Long Term Prediction [Process Count = ", count, "]")
    
    print("\n\n", prediction_matrix, "\n\n")

    graph_title = "../Images/" + model + "_sequential_prediction_demo.png"
    graph(prediction_matrix, 'red', graph_title, False)
    
    git_update()
