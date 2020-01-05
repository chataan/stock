
# model.py is the LSTM neural network that learns
# the trend of the stock, and predict future prices using Keras

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 

import time
import numpy as np
import tqdm as tqdm
from keras.models import load_model
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
            print('\n\n--------------------------------------------------------------\nKeras LSTM Prediction Model Session Created\n--------------------------------------------------------------\n')
        self.stock = stock_processor
        self.training_input = []
        self.training_output = []
        self.validation_input = []
        self.validation_output = []
    def preprocessing(self): 
        """ Packaging the processed stock data into 2 dimensional training arrays (numpy) """
        # upload the processed time series data to its distinct numpy arrays
        print('')
        loop = tqdm.tqdm(total = self.stock.amount_of_time_series(), position = 0, leave = False)
        for d in range(self.stock.amount_of_time_series()):
            loop.set_description('Packaging all processed time series data... ' .format(self.stock.amount_of_time_series()))
            time_series = self.stock.get_time_series(d)
            if time_series.get_dataset_label() == "TRAINING":
                self.training_input.append(time_series.spike_matrix())
                self.training_output.append(time_series.get_close_value())
            elif time_series.get_dataset_label() == "VALIDATING":
                self.validation_input.append(time_series.spike_matrix())
                self.validation_output.append(time_series.get_close_value())
            else:
                break
            loop.update(1)
            time.sleep(0.00001)
        self.training_input, self.training_output = np.array(self.training_input), np.array(self.training_output)
        self.training_input = np.reshape(self.training_input, (self.training_input.shape[0], self.training_input.shape[1], 1))
        self.validation_input, self.validation_output = np.array(self.validation_input), np.array(self.validation_output)
        self.validation_input = np.reshape(self.validation_input, (self.validation_input.shape[0], self.validation_input.shape[1], 1))
        print('')
        loop.close()
    def create_lstm_model(self, iterations=1000, batch_size=32):
        print("")
        lstm = Sequential() # initialize RNN
        # first layer of the LSTM (with dropout regularization)
        print(self.training_input.shape[0])
        print(self.training_input.shape[1])
        lstm.add(LSTM(units=self.stock.length_of_time_series(), return_sequences=True, input_shape=(self.training_input.shape[1], 1)))
        lstm.add(Dropout(0.2))
        # second layer of the LSTM (with dropout regularization)
        lstm.add(LSTM(units=self.stock.length_of_time_series(), return_sequences=True))
        lstm.add(Dropout(0.2))
        # third layer of the LSTM (with dropout regularization)
        lstm.add(LSTM(units=self.stock.length_of_time_series(), return_sequences=True))
        lstm.add(Dropout(0.2))
        # fourth layer of the LSTM (with dropout regularization)
        lstm.add(LSTM(units=self.stock.length_of_time_series()))
        lstm.add(Dropout(0.2))
        # the last output layer of the LSTM
        lstm.add(Dense(units=1))

        lstm.compile(optimizer='adam', loss='mean_squared_error')
        lstm.fit(self.training_input, self.training_output, epochs=iterations, batch_size=batch_size) # train each time series 1000 times
        lstm.fit(self.validation_input, self.validation_output, epochs=iterations/10, batch_size=batch_size) 

        # save the model
        model_name = self.stock.stock_name() + "_model.h5"
        model_json = lstm.to_json()
        with open("model.json", "w") as json_file:
            json_file.write(model_json)
        lstm.save_weights(model_name)
        print("\nCompleted Keras-LSTM Model Training! All data of the model is saved as a .json (LSTM layer) and .h5 (synapes) files!\n")
        