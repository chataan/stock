#!/usr/bin/env python3

import os 
from model import Model
from stock import upload
from service import download_stock, fetch_last_time_series, git_update
from financial import QUARTER, MONTH, STANDARD_SAMPLING_RANGE
from financial import moving_average, sampling, rescale

def sequential_prediction(stock, stock_id):
    predictor = Model(stock_id, "PREDICTION_MODEL")
    timeseries, final_close = fetch_last_time_series(stock, QUARTER)
    prediction_matrix = []

    for count in range(3):
        trend = moving_average(timeseries, MONTH)
        trend_close_diff = final_close - trend[len(trend) - 1]
        matrix = sampling(trend, 0, 2, STANDARD_SAMPLING_RANGE)
        timeseries.set_sampled_matrix(matrix)
        timeseries.normalize_timeseries()

        prediction = 0.00
        result = predictor.predict(timeseries)
        for i in range(result.shape[0]):
            for j in range(result.shape[1]):
                prediction = rescale(result[i][j], timeseries.minimum(), timeseries.maximum())
                # compare the distance of the last close price
                # and the moving average trend line to add bias to the prediction
                prediction += trend_close_diff
        prediction_matrix.append(prediction)
        raw = timeseries.raw_matrix()
        for i in range(0, len(raw)):
            raw[i] = rescale(raw[i], timeseries.minimum(), timeseries.maximum())
        del raw[0]
        raw.append(prediction)
        timeseries.set_raw_matrix(raw)
        count += 1
    return prediction_matrix

class Market:
    def __init__(self, name, list_of_stock_id, stock_collection_date):
        """ Argument <list_of_stocks> = 'string' list containing a list of stock IDs 
            Argument <stock_collection_date> = 'string', Format: 2020-02-29 """
        self.name = name
        self.stock_list = []
        self.stock_id_list = list_of_stock_id
        for id in self.stock_id_list:
            csv, i = download_stock(id, stock_collection_date)
            self.stock_list.append(upload(csv, True))

if __name__ == "__main__":
    os.system("clear")
    us_market = ['^ixic', '^gspc', '^nya', '^xax']
    US = Market('US Market', us_market, '2019-02-28')
    git_update()