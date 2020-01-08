
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
from algorithm import StockProcessor
from algorithm import rescale

class KerasPredictor:
    """ This predictor will generate a LSTM prediction model 
    based on the StockProcessor feeded in the class """
    def __init__(self, stock_processor=None, name=None):
        self.name = name
        self.loaded_model = None
        self.verification = None
        if type(stock_processor) != StockProcessor:
            self.verification = False
            return
        else:
            self.verification = True
            print('\n\n--------------------------------------------------------------------------------------------------------------------\nKeras LSTM Prediction Model Session Created\n--------------------------------------------------------------------------------------------------------------------\n')
        self.stock = stock_processor
        self.training_input = []
        self.training_output = []
        self.validation_input = []
        self.validation_output = []
        self.test_input = []
        self.test_output = []
        # run data preprocessing immediately
        self.preprocessing()
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
                self.test_input.append(time_series.spike_matrix())
                self.test_output.append(time_series.get_close_value())
            loop.update(1)
            time.sleep(0.00001)

        self.training_input, self.training_output = np.array(self.training_input), np.array(self.training_output)
        self.training_input = np.reshape(self.training_input, (self.training_input.shape[0], self.training_input.shape[1], 1))
        
        self.validation_input, self.validation_output = np.array(self.validation_input), np.array(self.validation_output)
        self.validation_input = np.reshape(self.validation_input, (self.validation_input.shape[0], self.validation_input.shape[1], 1))

        self.test_input, self.test_output = np.array(self.test_input), np.array(self.test_output)
        self.test_input = np.reshape(self.test_input, (self.test_input.shape[0], self.test_input.shape[1], 1))
        print('\n')
        loop.close()
        self.stock.terminate()
    def train_model(self, cells=50, iterations=1000, batch_size=32):
        print("")
        lstm = Sequential() # initialize RNN
        # first layer of the LSTM (with dropout regularization)
        lstm.add(LSTM(units=cells, return_sequences=True, input_shape=(self.training_input.shape[1], 1)))
        lstm.add(Dropout(0.2))
        # second layer of the LSTM (with dropout regularization)
        lstm.add(LSTM(units=cells))
        lstm.add(Dropout(0.2))
        # the last output layer of the LSTM
        lstm.add(Dense(units=1))

        lstm.compile(optimizer='adam', loss='mean_squared_error')
        lstm.fit(self.training_input, self.training_output, use_multiprocessing=True, epochs=iterations, batch_size=batch_size) # train each time series 1000 times
        lstm.fit(self.validation_input, self.validation_output, use_multiprocessing=True, epochs=int(iterations/10), batch_size=batch_size)

        # save the model
        model_name = self.name.lower() + "_model.h5"
        model_json = lstm.to_json()
        with open((self.name.lower() + "_model.json"), "w") as json_file:
            json_file.write(model_json)
        lstm.save_weights(model_name)
        print("\nCompleted Keras-LSTM Model Training! All data of the model is saved as a .json (LSTM layer) and .h5 (synapes) files!\n")
    def evaluate_test_set(self):
        json_file = open((self.name.lower() + '_model.json'), "r")
        loaded_model_json = json_file.read()
        json_file.close()

        loaded_model = model_from_json(loaded_model_json)
        loaded_model.load_weights((self.name + "_model.h5"))

        loaded_model.compile(optimizer='adam', loss='mean_squared_error', metrics=['accuracy'])
        accuracy = loaded_model.evaluate(self.test_input, self.test_output, verbose=0)
        print(self.name, ' Model %s =  [%.2f%%]' %(loaded_model.metrics_names[1], accuracy[1] * 100))
    def predict(self, stock_processor):
        x = []
        x.append(stock_processor.timeseries().spike_matrix())
        x = np.array(x)
        x = np.reshape(x, (x.shape[0], x.shape[1], 1))

        if self.loaded_model != None:
            """ THIS WILL ONLY BE EXECUTED WHEN ACTUALLY USING A PREDICTOR (ASSUMES IT ALREADY LOADED A MODEL) """
            prediction = self.loaded_model.predict(x)

            for d in range(prediction.shape[0]):
                for i in range(prediction.shape[1]):
                    prediction[d][i] = rescale(prediction[d][i], stock_processor.timeseries().minimum(), stock_processor.timeseries().maximum())
            print("Prediction = ", prediction)
        else:
            # load model
            json_file = open((self.name.lower() + '_model.json'), "r")
            loaded_model_json = json_file.read()
            json_file.close()

            loaded_model = model_from_json(loaded_model_json)
            loaded_model.load_weights((self.name.lower() + "_model.h5"))
            print("\nLoaded model for '", stock_processor.stock_name(), "'!\n")

            loaded_model.compile(optimizer='adam', loss='mean_squared_error')
            prediction = loaded_model.predict(x)

            for d in range(prediction.shape[0]):
                for i in range(prediction.shape[1]):
                    prediction[d][i] = rescale(prediction[d][i], stock_processor.timeseries().minimum(), stock_processor.timeseries().maximum())
            print("Prediction = ", prediction)
    # the below two functions will only be used when actually using the predictor
    def load(self, model_name):
        json_file = open(model_name + "_model.json", 'r')
        load = json_file.read()
        json_file.close()

        self.loaded_model = model_from_json(load)
        self.loaded_model.load_weights((model_name + "_model.h5"))
        self.loaded_model.compile(optimizer='adam', loss='mean_squared_error')
    def run(self, eval_stock, split_range, spike_sampling_range):
        """ argument(model) should be the NAME of the .json file of the model """
        sp = StockProcessor()
        sp.revert_to_predictor(eval_stock, split_range, spike_sampling_range)
        self.predict(sp)
