
import time
import stock as stock
import tqdm as tqdm
import matplotlib.pyplot as plt
import numpy as np

DATASET_LABEL = ["TRAINING", "VALIDATING", "TESTING"]

MONTH=31
QUARTER=91
YEAR=366

MINIMUM_SAMPLING_RANGE=3
DEFAULT_SAMPLING_RANGE=5 # Short term
MAXIMUM_SAMPLING_RANGE=10 # Long term

def normalize(matrix):
    """ MinMaxScaler to normalize matrix with high values """
    min = 10000
    max = -10000
    for val in matrix:
        if val < min:
            min = val
        elif val > max:
            max = val;
        else:
            pass
    for i in range(len(matrix)):
        matrix[i] = (matrix[i] - min) / (max - min)
    return matrix, min, max
def rescale(value, min, max):
    """ Reverse of a MinMaxScaler: scales up a certain value based on a min max value """
    return (value * (max - min)) + min 

class Dataset:
    def __init__(self, raw):
        self.dataset_label = ""
        self.raw, self.min, self.max = normalize(raw)
        self.final_close_value = self.raw[len(self.raw) - 1]
        self.trend = []
        del self.raw[len(raw) - 1] # exclude the last datapoint, which is the final close value
    def maximum(self):
        return self.max
    def minimum(self):
        return self.min
    def get_dataset_label(self):
        return self.dataset_label
    def get_close_value(self): # this is the labeled output of the corresponding time series data
        return self.final_close_value
    def raw_size(self):
        return len(self.raw)
    def raw_matrix(self):
        return self.raw
    def raw_datapoint(self, index):
        return self.raw[index]
    def trend_size(self):
        return len(self.trend)
    def trend_datapoint(self, index):
        return self.trend[index]
    def trend_matrix(self):
        return self.trend
    def append_trend_datapoint(self, val):
        self.trend.append(val)
    def set_dataset_label(self, label):
        self.dataset_label = label
    def set_trendline_matrix(self, matrix):
        self.trend = matrix

def partition_time_series(stock, timeseries_split_range):
    dataset = []
    for sets in range(0, (len(stock) - timeseries_split_range + 1)):
        raw = []
        for i in range(sets, (sets + timeseries_split_range)):
            raw.append(stock[i])
        dataset.append(Dataset(raw))
        raw = []
        
    # set breakpoints to split the dataset into three categories: training, validating, testing
    training_dataset_breakpoint = int((len(dataset) * 60) / 100)
    validation_dataset_breakpoint = training_dataset_breakpoint + int((len(dataset) * 30) / 100)
    testing_dataset_breakpoint = validation_dataset_breakpoint + int((len(dataset) * 10) / 100)

    amount_of_training_datasets = 0
    amount_of_validation_datasets = 0
    amount_of_testing_datasets = 0
    for i in range(len(dataset)):
        if i <= training_dataset_breakpoint:
            dataset[i].set_dataset_label("TRAINING")
            amount_of_training_datasets += 1
        elif (i > training_dataset_breakpoint) & (i <= validation_dataset_breakpoint):
            dataset[i].set_dataset_label("VALIDATING")
            amount_of_validation_datasets += 1
        else:
            dataset[i].set_dataset_label("TESTING")
            amount_of_testing_datasets += 1
    print("Completed stock time series partitioning! [Training = {0}, Validation = {1}, Testing = {2}]" .format(amount_of_training_datasets, amount_of_validation_datasets, amount_of_testing_datasets))
    print("Each time series data contains a total of {0} datapoints!\n" .format(dataset[0].raw_size()))
    return dataset

def reduction(time_series):
    """ Max pool reduction on trend line of time series """
    if (time_series.raw_size() % 2) != 0:
        for i in range(time_series.raw_size() % 2):
            time_series.append_trend_datapoint(0) # zero padding
    maximum = -1
    reduced = []
    for _range in range(0, time_series.raw_size() - 2, 2):
        for i in range(_range, _range + 2):
            if time_series.trend_datapoint(i) > maximum:
                maximum = time_series.trend_datapoint(i)
        reduced.append(maximum)
        maxmium = -1
    return reduced
def rolling_mean_trend(time_series, trend_window_range):
        """ Moving average analysis to detect trend in stock price variability """
        """ type(time_series) should be "Dataset" """
        """ RETURNS: Rolling mean trend 1D matrix, a prediction value """
        trend = []
        for _range in range(0, time_series.raw_size() - trend_window_range):
            avg = 0.00
            for i in range(_range, _range + trend_window_range):
                avg += time_series.raw_datapoint(i)
            avg /= trend_window_range
            trend.append(avg)
        for _range in range(time_series.raw_size() - trend_window_range, time_series.raw_size()):
            avg = 0.00
            for i in range(_range, time_series.raw_size()):
                avg += time_series.raw_datapoint(i)
            avg /= time_series.raw_size() - _range
            trend.append(avg)
        # compute linear slope of the last two datapoints to forecast the next possible datapoint
        y1, y2 = trend[len(trend) - 2], trend[len(trend) - 1]
        slope = y2 - y1
        bias = -slope + y1
        linear_prediction = slope * 3 + bias
        return trend, linear_prediction