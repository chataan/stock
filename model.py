
# model.py is the LSTM neural network that learns
# the trend of the stock, and predict future prices using Keras

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 

import time
import numpy as np
import tqdm as tqdm
from keras.models import model_from_json
from keras.models import load_model
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from keras.layers import Dropout
from financial import rescale

class KerasPredictor:
    """ This predictor will generate a LSTM prediction model """
    def __init__(self, dataset=None, name=None):
        self.name = name
        self.loaded_model = None
        self.training_input = []
        self.training_output = []
        self.validation_input = []
        self.validation_output = []
        self.test_input = []
        self.test_output = []
        if dataset != None:
            self.preprocessing(dataset)
    def preprocessing(self, dataset): 
        """ Packaging the processed stock data into 2 dimensional training arrays (numpy) """
        # upload the processed time series data to its distinct numpy arrays
        print('')
        loop = tqdm.tqdm(total = len(dataset), position = 0, leave = False)
        for d in range(len(dataset)):
            loop.set_description('Packaging all processed time series data... ' .format(len(dataset)))
            time_series = dataset[d]
            if time_series.get_dataset_label() == "TRAINING":
                self.training_input.append(time_series.trend_matrix())
                self.training_output.append(time_series.get_close_value())
            elif time_series.get_dataset_label() == "VALIDATING":
                self.validation_input.append(time_series.trend_matrix())
                self.validation_output.append(time_series.get_close_value())
            else:
                self.test_input.append(time_series.trend_matrix())
                self.test_output.append(time_series.get_close_value())
            loop.update(1)

        self.training_input, self.training_output = np.array(self.training_input), np.array(self.training_output)
        self.training_input = np.reshape(self.training_input, (self.training_input.shape[0], self.training_input.shape[1], 1))
        
        self.validation_input, self.validation_output = np.array(self.validation_input), np.array(self.validation_output)
        self.validation_input = np.reshape(self.validation_input, (self.validation_input.shape[0], self.validation_input.shape[1], 1))

        self.test_input, self.test_output = np.array(self.test_input), np.array(self.test_output)
        self.test_input = np.reshape(self.test_input, (self.test_input.shape[0], self.test_input.shape[1], 1))
        print('\n')
        loop.close()
    def train(self, cells=None, multiprocessing=True, iterations=1000, batch_size=32):
        print("")
        if cells == None:
            int(self.training_input.shape[1] / 3)
        lstm = Sequential() # initialize RNN
        # first layer of the LSTM (with dropout regularization)
        lstm.add(LSTM(units=cells, return_sequences=True, input_shape=(self.training_input.shape[1], 1)))
        lstm.add(Dropout(0.2))
        # second layer of the LSTM (with dropout regularization)
        lstm.add(LSTM(units=cells))
        lstm.add(Dropout(0.2))
        # the last output layer of the LSTM
        lstm.add(Dense(units=1))

        lstm.compile(optimizer='adam', loss='mean_squared_error', metrics=['accuracy'])
        lstm.fit(self.training_input, self.training_output, use_multiprocessing=multiprocessing, epochs=iterations, batch_size=batch_size) # train each time series 1000 times
        lstm.fit(self.validation_input, self.validation_output, use_multiprocessing=multiprocessing, epochs=int(iterations/10), batch_size=batch_size)

        # save the model
        model_name = self.name.lower() + "_model.h5"
        model_json = lstm.to_json()
        with open((self.name.lower() + "_model.json"), "w") as json_file:
            json_file.write(model_json)
        lstm.save_weights(model_name)
        print("\nCompleted Keras-LSTM Model Training! All data of the model is saved as a .json (LSTM layer) and .h5 (synapes) files!\n")

        # load the model, evaluate test sets
        json_file = open((self.name.lower() + '_model.json'), "r")
        loaded_model_json = json_file.read()
        json_file.close()

        loaded_model = model_from_json(loaded_model_json)
        loaded_model.load_weights((self.name + "_model.h5"))

        loaded_model.compile(optimizer='adam', loss='mean_squared_error', metrics=['accuracy'])
        accuracy = loaded_model.evaluate(self.test_input, self.test_output, verbose=0)
        print(self.name, ' Model %s =  [%.2f%%]' %(loaded_model.metrics_names[1], accuracy[1] * 100))
           