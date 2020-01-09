
import time
import stock as stock
import tqdm as tqdm
import matplotlib.pyplot as plt

DATASET_LABEL = ["TRAINING", "VALIDATING", "TESTING"]

TRAIN=0
PREDICT=1

MONTH = 40 
QUARTER = 90 # 3 months
YEAR = 365 # a year

MINIMUM_SAMPLING_RANGE = 3
DEFAULT_SAMPLING_RANGE = 4
MAXIMUM_SAMPLING_RANGE = 5

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
        self.raw, self.min, self.max = normalize(raw)
        self.final_close_value = self.raw[len(self.raw) - 1]
        self.spike_detected_matrix = []
        self.trend = []
        self.variability_slope = 0.00 # the slope of a linear segment that links the first and last value in the raw data
        self.increase_decrease_ratio = 0.00 # frequency of price increase : frequency of price decrease (stability of the stock's variability)
        self.average_price_variablity = 0.00 # average price variability in raw data
        self.data_analysis_confidence_rate = 0.00 # based on the data analysis values, express a confidence rate for the prediction
        self.dataset_label = ""
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
    def spike_datapoint(self, index):
        return self.spike_detected_matrix[index]
    def trend_datapoint(self, index):
        return self.trend[index]
    def spike_matrix(self):
        return self.spike_detected_matrix
    def trend_matrix(self):
        return self.trend
    def set_dataset_label(self, label):
        self.dataset_label = label
    def set_raw_matrix(self, matrix):
        self.raw = matrix
    def set_spike_detected_matrix(self, matrix):
        self.spike_detected_matrix = matrix
    def set_trendline_matrix(self, matrix):
        self.trend = matrix

class StockProcessor:
    def __init__(self, target_stock, timeseries_split_range, trend_window_range, spike_sampling_range=DEFAULT_SAMPLING_RANGE, log=True):
        self.log = log
        self.mode=TRAIN
        self.verification = None
        if type(target_stock) != stock.Stock:
            print("ERROR: Given stock does not match the required stock.Stock data type! All future processes are disabled")
            self.verification = False # this will disable the StockProcessor from running any processes to prevent errors
        else:
            self.verification = True
        self.target_stock = target_stock
        self.timeseries_split_range = timeseries_split_range
        self.trend_window_range = trend_window_range
        self.sampling_range = spike_sampling_range
        self.dataset = []
        self.time_series = None # will only be used in prediction mode
        # immediately run the processor
        self.run()
    def revert_to_predictor(self, target_stock, timeseries_split_range, trend_window_range, sampling_range):
        """ Initialize all data contained in the stock processor, upload new information """
        self.terminate()
        self.mode = PREDICT
        self.verification = True
        self.target_stock = target_stock
        self.timeseries_split_range = timeseries_split_range
        self.trend_window_range = trend_window_range
        self.sampling_range = sampling_range
        self.time_series = None
        # immediately run process
        self.run()
    def terminate(self):
        """ Terminate session: free all arrays/memory allocated by the processor """
        del self.dataset[:]
        self.target_stock.terminate()
    def partition_time_series(self):
        raw = []
        for sets in range(0, (self.target_stock.amount_of_datapoints() - self.timeseries_split_range + 1)):
            for i in range(sets, (sets + self.timeseries_split_range)):
                raw.append(self.target_stock.datapoint(i))
            self.dataset.append(Dataset(raw))
            raw = []
        
        # set breakpoints to split the dataset into three categories: training, validating, testing
        training_dataset_breakpoint = int((len(self.dataset) * 60) / 100)
        validation_dataset_breakpoint = training_dataset_breakpoint + int((len(self.dataset) * 30) / 100)
        testing_dataset_breakpoint = validation_dataset_breakpoint + int((len(self.dataset) * 10) / 100)

        amount_of_training_datasets = 0
        amount_of_validation_datasets = 0
        amount_of_testing_datasets = 0
        for i in range(len(self.dataset)):
            if i <= training_dataset_breakpoint:
                self.dataset[i].set_dataset_label("TRAINING")
                amount_of_training_datasets += 1
            elif (i > training_dataset_breakpoint) & (i <= validation_dataset_breakpoint):
                self.dataset[i].set_dataset_label("VALIDATING")
                amount_of_validation_datasets += 1
            else:
                self.dataset[i].set_dataset_label("TESTING")
                amount_of_testing_datasets += 1
        print("Completed stock time series partitioning! [Training = {0}, Validation = {1}, Testing = {2}]" .format(amount_of_training_datasets, amount_of_validation_datasets, amount_of_testing_datasets))
        print("Each time series data contains a total of {0} datapoints!" .format(self.dataset[0].raw_size()))
        self.target_stock.terminate() # Stock Class is no longer needed
    def spike_detection(self, matrix):
        """ spike detection algorithm that extracts datapoints with  high alteration values within a segmentation range """
        if  (self.sampling_range < MINIMUM_SAMPLING_RANGE) | (self.sampling_range > MAXIMUM_SAMPLING_RANGE):
            print("\nWARNING: Specified spike sampling range is out of limits! Reverting to default sampling range...")
            self.sampling_range = DEFAULT_SAMPLING_RANGE
        sampled = []
        spike_start = 0
        spike_start_index = 0
        spike_end = 0
        spike_end_index = 0
        spike_midpoint = 0
        spike_midpoint_index = 0
        maximum_variability = -10000
        for _range in range(0, len(matrix) - self.sampling_range, self.sampling_range):
            for i in range(_range, (_range + self.sampling_range)):
                if (i + 1) > len(matrix):
                    pass
                else:
                    if abs(matrix[i] - matrix[i + 1]) > maximum_variability:
                        spike_start, spike_start_index = matrix[i], i
                        spike_end, spike_end_index = matrix[i + 1], i + 1
            # between the spike points detected beforehand, sample out the maximum value between those two
            midpoint_max = -10000
            for i in range(spike_start_index, spike_end_index):
                if matrix[i] > midpoint_max:
                    midpoint_max =  matrix[i]
            # push in all the sampled datapoints
            sampled.append(spike_start)
            sampled.append(midpoint_max)
            sampled.append(spike_end)
        return matrix
    def rolling_mean_trend(self, matrix):
        """ Moving average analysis to detect trend in stock price variability """
        """ RETURNS: Rolling mean trend 1D matrix, a prediction value """
        trend = []
        for _range in range(0, len(matrix) - self.trend_window_range):
            avg = 0.00
            for i in range(_range, _range + self.trend_window_range):
                avg += matrix[i]
            avg /= self.trend_window_range
            trend.append(avg)
        for _range in range(len(matrix) - self.trend_window_range, len(matrix)):
            #print(_range)
            avg = 0.00
            for i in range(_range, len(matrix)):
                avg += matrix[i]
            avg /= len(matrix) - _range
            trend.append(avg)
        # level up the trend line on top of the actual values
        level_up = abs(matrix[0] - trend[0])
        return trend
    def run(self):
        if self.mode == TRAIN:
            if self.verification == False:
                print("StockProcessor was disabled for future processes due to a non-matching data type for the target stock!")
                return
            else:
                self.partition_time_series()
                # apply the spike detection algorithm on all stock datasets
                print('')
                if self.log == True:
                    loop = tqdm.tqdm(total = len(self.dataset), position = 0, leave = False)
                for data in self.dataset:
                    if self.log == True:
                        loop.set_description('Applying spike detection/trend line analysis on time series... ' .format(len(self.dataset)))
                    data.set_trendline_matrix(self.rolling_mean_trend(data.raw_matrix()))
                    if self.log == True:
                        loop.update(1)
                    time.sleep(0.0000001)
                print('\nCompleted spike detection!')
                if self.log == True:
                    loop.close()
                count = []
                for i in range(self.dataset[0].raw_size()):
                    count.append(i)
                plt.plot(count, self.dataset[0].raw_matrix(), color='green')
                plt.plot(count, self.dataset[0].trend_matrix(), color='red')
                plt.xlabel('datapoints')
                plt.ylabel('val')
                plt.title('test')
                plt.show()
                time.sleep(3)
        else:
            print('\n                                           RUNNING PREDICTION MODE')
            raw = []
            for i in range(self.timeseries_split_range):
                raw.append(self.target_stock.datapoint(i).price())
            self.time_series = Dataset(raw)
            self.time_series = self.spike_detection(self.time_series)
    def stock_name(self):
        return self.target_stock.stock_name()
    def amount_of_time_series(self):
        return len(self.dataset)
    def length_of_time_series(self):
        return len(self.dataset[0].spike_matrix())
    def get_time_series(self, index):
        return self.dataset[index]
    def timeseries(self):
        return self.time_series
