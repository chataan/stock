
import os
import time
from financial import rescale
from financial import MONTH, QUARTER, YEAR
from financial import MINIMUM_SAMPLING_RANGE, STANDARD_SAMPLING_RANGE, MAXIMUM_SAMPLING_RANGE
from financial import fetch_last_time_series, sampling, rolling_mean_trend
from model import Model

def select_model():
    os.system("clear")
    files = []
    for r, d, f in os.walk("."):
        for file in f:
            if '.h5' in file:
                file = str(file)
                file = file[:-9]
                files.append(file)
    select = -1
    while (select < 0) or (select > len(files)):
        print("\nSelect a model number:\n")
        for i in range(len(files)):
            print("     [{0}]:   {1}" .format(i, files[i]))
    
        print("\n")
        select = int(input(": "))

        if (select < 0) or (select > len(files)):
            print("\nPlease select a model number listed above!\n")
            time.sleep(2)
            os.system("clear")
    print("\n", files[0], "model selected!!")
    return files[0]

def run(stock, model_name):
    test = fetch_last_time_series(stock, QUARTER)

    print("Running time series processing... ", end="")
    matrix, prediction = rolling_mean_trend(test, MONTH)
    matrix = sampling(matrix, STANDARD_SAMPLING_RANGE)
    test.set_sampled_matrix(matrix)
    print("DONE!\n")

    predictor = Model(model_name)
    result = predictor.predict(test)
    
    keras_prediction = 0.00
    for i in range(result.shape[0]):
        for j in range(result.shape[1]):
            keras_prediction = rescale(result[i][j], test.minimum(), test.maximum())
    
    # output the predictions
    prediction = rescale(prediction, test.minimum(), test.maximum())
    print("Trend line prediction = [", prediction, "]")
    print("Keras Model prediction = [", keras_prediction, "]")
