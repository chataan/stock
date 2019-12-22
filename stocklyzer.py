
import time
import stock as stock
from sklearn import preprocessing

DATASET_LABEL = ["TRAINING", "VALIDATING", "TESTING"]

MINIMUM_SAMPLING_RANGE = 3
DEFAULT_SAMPLING_RANGE = 5
MAXIMUM_SAMPLING_RANGE = 6

class Dataset:
    def __init__(self, raw):
        self.raw = raw
        self.spike_detected_matrix = []
        self.final_close_value = self.raw[len(self.raw) - 1] # expected output
        self.dataset_label = ""
        del self.raw[len(raw) - 1] # exclude the last datapoint, which is the final close value
    def set_dataset_label(self, label):
        self.dataset_label = label
    def normalize(self):
        """ MinMaxScaler """
        min = 10000
        max = -10000
        for val in self.raw:
            if val < min:
                min = val
            elif val > max:
                max = val
            else:
                pass
        for i in range(len(self.raw)):
            self.raw[i] = (self.raw[i] - min) / (max - min)
    def raw_size(self):
        return len(self.raw)
    def raw_matrix(self):
        return self.raw
    def raw_datapoint(self, index):
        return self.raw[index]
    def append_spike_datapoint(self, val):
        self.spike_detected_matrix.append(val)

class StockProcessor:
    def __init__(self, target_stock, split_range, spike_sampling_range):
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
        for i in range(self.target_stock.amount_of_datapoints()):
            raw.append(self.target_stock.datapoint(i).price())
            if i % self.split_range == 0:
                self.dataset.append(Dataset(raw))
                raw = []
        # set breakpoints to split the dataset into three categories: training, validating, testing
        self.training_dataset_breakpoint = int((len(self.dataset) * 60) / 100)
        self.validation_dataset_breakpoint = self.training_dataset_breakpoint + int((len(self.dataset) * 20) / 100)
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
            self.dataset[i].normalize()
        print("Completed stock data pre-processing! [Training = {0}, Validation = {1}, Testing = {2}]" .format(self.amount_of_training_datasets, self.amount_of_validation_datasets, self.amount_of_testing_datasets))
        time.sleep(1)
    def spike_detection(self, dataset):
        """ deploy a spike detection algorithm that extracts datapoints with 
        high alteration values within a segmentation range """
        if (self.spike_sampling_range < MINIMUM_SAMPLING_RANGE) | (self.spike_sampling_range > MAXIMUM_SAMPLING_RANGE):
            print("\nWARNING: Specified spike sampling range is out of limits! Reverting to default sampling range...")
            self.spike_sampling_range = DEFAULT_SAMPLING_RANGE
    def run(self):
        self.prepare_dataset()
        for data in self.dataset:
            data = self.spike_detection(data)