
# model.py is the LSTM neural network that learns
# the trend of the stock, and predict future prices using Keras

import numpy as np
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from keras.layers import Dropout
from algorithm import StockProcessor

class KerasPredictor:
    """ This predictor will generate a LSTM prediction model 
    based on the StockProcessor feeded in the class """
    def __init__(self, stock_processor, name=None):
        self.name = name
        self.verification = None
        if type(stock_processor) != StockProcessor:
            print("ERROR: An unknown data type was given! All processes are disabled!")
            self.verification = False
            return
        else:
            self.verification = True
        self.stock = stock_processor
        self.training_input = None
        self.training_output = None
    def preprocessing(self): 
        """ Packaging the processed stock data into 2 dimensional training arrays (numpy) """
        self.training_input = np.zeros([self.stock.amount_of_time_series(), self.stock.length_of_time_series()])
        self.training_output = np.zeros([self.stock.amount_of_time_series()])
        # upload the processed time series data to its distinct numpy arrays
        for d in range(self.stock.amount_of_time_series()):
            time_series = self.stock.get_time_series(d)
            self.training_output[d] = time_series.get_close_value()
            for i in range(self.stock.length_of_time_series()):
                self.training_input[d][i] = time_series.spike_datapoint(i) 