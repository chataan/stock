
import time
import stock as stock
import tqdm as tqdm

DATASET_LABEL = ["TRAINING", "VALIDATING", "TESTING"]

SHORT_TERM = 30
LONG_TERM = 365

MINIMUM_SAMPLING_RANGE = 3
DEFAULT_SAMPLING_RANGE = 5
MAXIMUM_SAMPLING_RANGE = 6

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
    return matrix
def rescale(value, min, max):
    """ Reverse of a MinMaxScaler: scales up a certain value based on a min max value """
    return (value * (max - min)) + min 

class Dataset:
    def __init__(self, raw):
        self.raw = raw
        self.min = 0
        self.max = 0
        self.spike_detected_matrix = []
        self.final_close_value = self.raw[len(self.raw) - 1] # expected output
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
    def set_dataset_label(self, label):
        self.dataset_label = label
    def raw_size(self):
        return len(self.raw)
    def raw_matrix(self):
        return self.raw
    def raw_datapoint(self, index):
        return self.raw[index]
    def set_raw_matrix(self, matrix):
        for i in range(len(matrix)):
            self.raw[i] = matrix[i]
    def append_spike_datapoint(self, val):
        self.spike_detected_matrix.append(val)
    def spike_matrix(self):
        return self.spike_detected_matrix
    def set_variability_slope(self, val):
        self.variability_slope = val
    def set_increase_decrease_ratio(self, val):
        self.increase_decrease_ratio = val
    def set_average_price_variability(self, val):
        self.average_price_variablity = val
    def compute_confidence_rate(self):
        # sum up the variability slope, increase/decrease ratio, and avg. price variability values
        # average them as the confidence rate (i.e., judgement) on the prediction that will be made
        # this will typically return a value between 0.0 ~ 1.0
        # if it exceeds 1.0, it means the dataset is confident on is prediction in accordance with the data analysis done regarding the dataset
        self.data_analysis_confidence_rate = (self.variability_slope + self.increase_decrease_ratio + self.average_price_variablity) / 3

class StockProcessor:
    def __init__(self, target_stock, split_range, spike_sampling_range):
        self.verification = None
        if type(target_stock) != stock.Stock:
            print("ERROR: Given stock does not match the required stock.Stock data type! All future processes are disabled")
            self.verification = False # this will disable the StockProcessor from running any processes to prevent errors
        else:
            self.verification = True
        self.target_stock = target_stock
        self.split_range = split_range
        self.spike_sampling_range = spike_sampling_range
        self.dataset = []
        self.training_dataset_breakpoint = None
        self.validation_dataset_breakpoint = None
        self.testing_dataset_breakpoint = None
        self.amount_of_training_datasets = 0
        self.amount_of_validation_datasets = 0
        self.amount_of_testing_datasets = 0
    def prepare_dataset(self):
        for i in range(self.target_stock.amount_of_datapoints() % self.split_range):
            self.target_stock.delete_datapoint(i)
        raw = []
        for sets in range(0, (self.target_stock.amount_of_datapoints() - self.split_range + 1)):
            for i in range(sets, (sets + self.split_range)):
                raw.append(self.target_stock.datapoint(i).price())
            self.dataset.append(Dataset(raw))
            raw = []
        
        # set breakpoints to split the dataset into three categories: training, validating, testing
        self.training_dataset_breakpoint = int((len(self.dataset) * 60) / 100)
        self.validation_dataset_breakpoint = self.training_dataset_breakpoint + int((len(self.dataset) * 30) / 100)
        self.testing_dataset_breakpoint = self.validation_dataset_breakpoint + int((len(self.dataset) * 10) / 100)

        for i in range(len(self.dataset)):
            if i <= self.training_dataset_breakpoint:
                self.dataset[i].set_dataset_label("TRAINING")
                self.amount_of_training_datasets += 1
            elif (i > self.training_dataset_breakpoint) & (i <= self.validation_dataset_breakpoint):
                self.dataset[i].set_dataset_label("VALIDATING")
                self.amount_of_validation_datasets += 1
            else:
                self.dataset[i].set_dataset_label("TESTING")
                self.amount_of_testing_datasets += 1
            # normalize the raw stock data of all datasets
            self.dataset[i].set_raw_matrix(normalize(self.dataset[i].raw_matrix()))
        print("Completed stock dataset partitioning! [Training = {0}, Validation = {1}, Testing = {2}]" .format(self.amount_of_training_datasets, self.amount_of_validation_datasets, self.amount_of_testing_datasets))
        print("Each dataset contains a total of {0} stock datapoints!" .format(self.dataset[0].raw_size()))
        time.sleep(1)
    def spike_detection(self, dataset):
        """ deploy a spike detection algorithm that extracts datapoints with 
        high alteration values within a segmentation range """
        if (self.spike_sampling_range < MINIMUM_SAMPLING_RANGE) | (self.spike_sampling_range > MAXIMUM_SAMPLING_RANGE):
            print("\nWARNING: Specified spike sampling range is out of limits! Reverting to default sampling range...")
            self.spike_sampling_range = DEFAULT_SAMPLING_RANGE
        temp1 = 0
        temp2 = 0
        maximum_variability = -10000
        for _range in range(0, dataset.raw_size() - self.spike_sampling_range, self.spike_sampling_range):
            for i in range(_range, (_range + self.spike_sampling_range - 1)):
                if (i + 1) > dataset.raw_size():
                    pass
                else:
                    if abs(dataset.raw_datapoint(i) - dataset.raw_datapoint(i + 1)) > maximum_variability:
                        temp1 = dataset.raw_datapoint(i)
                        temp2 = dataset.raw_datapoint(i + 1)
            dataset.append_spike_datapoint(temp1)
            dataset.append_spike_datapoint(temp2)
        return dataset
    def variability_slope_analysis(self, dataset):
        """ return the slope of a linear segment connecting the first and last raw stock datapoint
        this represents the steadiness of the stock's variability or price change
        higher the value --> higher stock increase """
        variability = (rescale(dataset.raw_datapoint(dataset.raw_size() - 1), dataset.minimum(), dataset.maximum()) - rescale(dataset.raw_datapoint(0), dataset.minimum(), dataset.maximum())) / dataset.raw_size()
        # threshold the value
        if variability < 0.00:
            variability = 0.00
        elif variability > 1.00:
            variability = 1.00
        else:
            pass
        return variability
    def increase_decrease_ratio(self, dataset):
        """ calculate the frequency difference of the stock's price increase/decrease 
        (iterations of increase : iterations of decrease) --> higher score = higher stock increase frequency """
        increase_iterations = 0
        decrease_iterations = 0
        for i in range(dataset.raw_size() - 1):
            if dataset.raw_datapoint(i) < dataset.raw_datapoint(i + 1):
                increase_iterations += 1
            elif dataset.raw_datapoint(i) > dataset.raw_datapoint(i + 1):
                decrease_iterations += 1
            else:
                pass
        # threshold the value (this value cannot be lower than zero, but can exceed 1.00)
        ratio = increase_iterations / decrease_iterations
        if ratio > 1.00:
            ratio = 1.00
        else:
            pass
        return ratio
    def average_price_variability(self, dataset):
        """ calculate the average change (variability) of the stock's value 
        --> evaluates the consistency/stableness of growth (lower the score, the more steady growth/variability in stock price """
        # rescale the raw matrix
        rescaled = []
        for val in dataset.raw_matrix():
            rescaled.append(rescale(val, dataset.minimum(), dataset.maximum()))
        price_variability = 0
        for i in range(len(rescaled) - 1):
            price_variability += abs(rescaled[i + 1] - rescaled[i])
        # threshold the value (this value cannot be lower than zero, but can exceed 1.00)
        if price_variability > 1.00:
            price_variability = 1.00
        else:
            pass
        return price_variability
    def data_analysis(self, dataset):
        dataset.set_variability_slope(self.variability_slope_analysis(dataset))
        dataset.set_increase_decrease_ratio(self.increase_decrease_ratio(dataset))
        dataset.set_average_price_variability(self.average_price_variability(dataset))
        dataset.compute_confidence_rate()
        #print(self.variability_slope_analysis(dataset), self.increase_decrease_ratio(dataset), self.average_price_variability(dataset))
        return dataset
    def run(self):
        if self.verification == False:
            print("StockProcessor was disabled for future processes due to a non-matching data type for the target stock!")
            return
        else:
            self.prepare_dataset()
            # apply the spike detection algorithm on all stock datasets
            print('')
            loop = tqdm.tqdm(total = len(self.dataset), position = 0, leave = False)
            for data in self.dataset:
                loop.set_description('Applying spike detection algorithm on stock dataset... ' .format(len(self.dataset)))
                data = self.spike_detection(data)
                loop.update(1)
                time.sleep(0.001)
            print('\nCompleted spike detection!')
            loop.close()
            # run data analysis algorithm on each dataset
            print('')
            loop = tqdm.tqdm(total = len(self.dataset), position = 0, leave = False)
            for data in self.dataset:
                loop.set_description('Running data analysis on stock dataset... ' .format(len(self.dataset)))
                data = self.data_analysis(data)
                loop.update(1)
                time.sleep(0.0001)
            print('\nCompleted data analysis!')
