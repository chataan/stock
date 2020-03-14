#!/usr/bin/env python3

from service import graph
from service import download_stock
from service import partition_time_series
from financial import moving_average, sampling

def regression(matrix):
    """ my own implementation of linear regression on a stock matrix """
    """ this is crappy. don't take this seriously """
    # set initial slope and bias based on the end points of the matrix
    end_point_slope = (matrix[len(matrix) - 1] - matrix[0]) / len(matrix)
    end_point_bias = matrix[0]

    high, high_index = -1, 0
    low, low_index = 10000000, 0
    for i in range(len(matrix)):
        if matrix[i] > high:
            high = matrix[i]
            high_index = i
        else:
            low = matrix[i]
            low_index = i

    high_low_slope = 0.00
    high_low_slope = (matrix[high_index] - matrix[low_index]) / (high_index - low_index)
    
    regression_slope = (high_low_slope + end_point_slope) / 2
    return regression_slope, end_point_bias

if __name__ == "__main__":
    stock, id = download_stock()
    dataset = partition_time_series(stock, 150)
    trend = []

    for timeseries in dataset:
        line = moving_average(timeseries, 5)
        trend.append(sampling(line, 0, 2, 3))

    slope, bias = regression(trend[0])
    line = [i * slope + bias for i in range(len(trend[0]))]

    print(slope)

    graph(trend[15], "green", "trend.png", False)
    graph(line, "red", "trend.png", False)