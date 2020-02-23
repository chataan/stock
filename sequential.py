#!/usr/bin/env python3

import os
from stock import upload
from service import graph, select_model, download_stock, sequential_prediction, git_update
from financial import fetch_last_time_series, rescale, moving_average, sampling, QUARTER, MONTH, STANDARD_SAMPLING_RANGE
from model import Model

if __name__ == "__main__":
    os.system('clear')
    model = select_model()
    print("Model = [", model, "]\n")

    path, id = download_stock()
    st = upload(path, True)

    predictor = Model(model, "PREDICTION_MODEL")
    timeseries = fetch_last_time_series(st, QUARTER)
    prediction_matrix = []
    
    for count in range(3):
        matrix = moving_average(timeseries, MONTH)
        matrix = sampling(matrix, 0, 2, STANDARD_SAMPLING_RANGE)
        timeseries.set_sampled_matrix(matrix)
        timeseries.normalize_timeseries()

        prediction = 0.00
        result = predictor.predict(timeseries)
        for i in range(result.shape[0]):
            for j in range(result.shape[1]):
                prediction = rescale(result[i][j], timeseries.minimum(), timeseries.maximum())
        
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

    graph_title = "Images/" + model + "_sequential_prediction_demo.png"
    graph(prediction_matrix, 'red', graph_title, False)
    
    git_update()
