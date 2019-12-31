
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
    def __init__(self, stock_processor):
        self.verification = None
        if type(stock_processor) != StockProcessor:
            print("ERROR: An unknown data type was given! All processes are disabled!")
            self.verification = False
            return
        else:
            self.verification = True
        self.stock = stock_processor
        self.training_input = []
        self.training_output = []
    def preprocessing(self): 
        """ Packaging the processed stock data into 2 dimensional training arrays (numpy) """
        