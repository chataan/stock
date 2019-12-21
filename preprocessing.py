
import stock as stock

""" split stock into separate datasets --> spike detection algorithm  """ 

class Dataset:
    def __init__(self, raw):
        self.raw = raw
        self.spike_detected_matrix = []
        self.final_close_value = self.raw[len(self.raw) - 1]

class StockProcessor:
    def __init__(self, target_stock, split_range, spike_sampling_range):
        self.target_stock = target_stock
        self.split_range = split_range
        self.spike_sampling_range = spike_sampling_range
        self.dataset = []
    def run(self):
        for i in range(self.target_stock.amount_of_datapoints() % self.split_range):
            self.target_stock.delete_datapoint(i)
        for i in range(self.target_stock.amount_of_datapoints()):
            raw = []
            raw.append(self.target_stock.datapoint(i).price())
            if i % self.split_range == 0:
                self.dataset.append(Dataset(raw))
                del raw[:]
                i -= 1
        