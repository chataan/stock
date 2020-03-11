
# model.py is the LSTM neural network that learns
# the trend of the stock, and predict future prices using Keras

import logging, os

logging.disable(logging.WARNING)
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

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

def preprocessing(dataset): 
        """ Packaging the processed stock data into 2 dimensional training arrays (numpy) """
        # upload the processed time series data to its distinct numpy arrays
        print('')
        training_input = []
        training_output = []
        validation_input = []
        validation_output = []
        loop = tqdm.tqdm(total = len(dataset), position = 0, leave = False)
        for d in range(len(dataset)):
            loop.set_description('Packaging all processed time series data... ' .format(len(dataset)))
            time_series = dataset[d]
            if time_series.get_dataset_label() == "TRAINING":
                training_input.append(time_series.sampled_matrix())
                training_output.append(time_series.get_close_value())
            else:
                validation_input.append(time_series.sampled_matrix())
                validation_output.append(time_series.get_close_value())
            loop.update(1)

        training_input, training_output = np.array(training_input), np.array(training_output)
        training_input = np.reshape(training_input, (training_input.shape[0], training_input.shape[1], 1))
        validation_input, validation_output = np.array(validation_input), np.array(validation_output)
        validation_input = np.reshape(validation_input, (validation_input.shape[0], validation_input.shape[1], 1))
        print('\n')
        loop.close()
        return training_input, training_output, validation_input, validation_output
def trend_model_preprocessing(dataset):
    training_input = []
    training_output = []
    validation_input = []
    validation_output = []
    training_break_point = int((len(dataset) * 60) / 100)
    for i in range(0, len(dataset) - 7):
        if i < training_break_point - 7:
            training_input.append(dataset[i].sampled_matrix())
            output = dataset[i + 7].sampled_matrix()
            if output[len(output) - 1] - output[0] > 0: # increasing trend
                training_output.append(1.00) # 1.00 for INCREASING TREND
            else:
                training_output.append(0.00) # 0.00 for DECREASING TREND
        else:
            validation_input.append(dataset[i].sampled_matrix())
            output = dataset[i + 7].sampled_matrix()
            if output[len(output) - 1] - output[0] > 0: # increasing trend
                validation_output.append(1.00) # 1.00 for INCREASING TREND
            else:
                validation_output.append(0.00) # 0.00 for DECREASING TREND
    training_input, validation_input = np.array(training_input), np.array(validation_input)
    training_input = np.reshape(training_input, (training_input.shape[0], training_input.shape[1], 1))
    validation_input = np.reshape(validation_input, (validation_input.shape[0], validation_input.shape[1], 1))
    return training_input, training_output, validation_input, validation_output

class Model:
    def __init__(self, model_name, model_type):
        """ model_name should be the stock name (ex: google, microsoft ...) 
        __init__ will load the Keras model (.json, .h5) """
        self.model = None
        self.model_name = model_name.lower()
        self.model_type = model_type
        self.exists = False
        if self.model_type == "PREDICTION_MODEL":
            try:
                self.json_file = open("../prediction/Models/" + model_name + "_model.json", "r")
                self.loaded_json = self.json_file.read()
                self.model = model_from_json(self.loaded_json)
                self.model.load_weights("../prediction/Models/" + self.model_name + "_model.h5")
                self.json_file.close()
                self.exists = True
            except IOError:
                pass
    def valid(self):
        return self.exists
    def update(self, dataset, use_multiprocessing=True, iterations=100, batch_size=32):
        training_input = []
        training_output = []
        validation_input = []
        validation_output = []
        self.model.compile(optimizer='adam', loss='mean_squared_error')
        if self.model_type == "PREDICTION_MODEL":
            training_input, training_output, validation_input, validation_output = preprocessing(dataset)
        else:
            training_input, training_output, validation_input, validation_output = trend_model_preprocessing(dataset)
        # update the model
        self.model.fit(training_input, training_output, use_multiprocessing=use_multiprocessing, epochs=iterations,  validation_data=(training_input, training_output))
        self.model.fit(validation_input, validation_output, use_multiprocessing=use_multiprocessing, epochs=iterations)
        # save the updated model
        name = self.model_name + "_model.h5"
        json = self.model.to_json()
        with open((self.model_name + "_model.json"), "w") as json_file:
            json_file.write(json)
        self.model.save_weights(name)
        print("\nCompleted Keras-LSTM Model Update!\n")
        if self.model_type == "PREDICTION":
            os.system("mv *.h5 ../prediction/Models")
            os.system("mv *.json ../prediction/Models")
    def predict(self, data):
        """ data should be a time series """
        x = []
        x.append(data.sampled_matrix())
        x = np.array(x)
        x = np.reshape(x, (x.shape[0], x.shape[1], 1))

        result = self.model.predict(x)
        return result