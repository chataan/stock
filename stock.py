
import os
import time as time
import tqdm as tqdm
import matplotlib.pyplot as plt
from datetime import datetime

YEAR=0
MONTH=1
DATE=2
OPEN=3
CLOSE=7

class Stock:
    def __init__(self, name=None, path=None, graph=False, log=False):
        self.log = log
        self.name = name
        self.path = path
        self.raw = [] # just the price values
        self.upload_stock_data()
        self.count = []
        if graph == True:
            for i in range(len(self.datapoints)):
                if graph == True:
                    self.count.append(i)
            # show and save a graph of the stock
            stock_graph = str(datetime.today().strftime("%Y-%m-%d")) + "-" + self.name + ".png"
            plt.plot(self.count, self.raw)
            plt.xlabel('Datapoint Count')
            plt.ylabel('Stock Price')
            plt.title(stock_graph)
            plt.show()
        else:
            pass
    def terminate(self):
        del self.count[:]
        del self.raw[:]
    def stock_name(self):
        return self.name
    def upload_stock_data(self):
        """ Upload datapoints of a stock """
        uploaded = []
        data = []
        file = open(self.path, "r")
        info = file.readlines()
        for x in info:
            data.append(x)
            data[len(data) - 1] = data[len(data) - 1].replace("-", ",")
        del data[0] # delete the line: "Date,Open,High,Low,Close,Adj Close,Volume" on the .csv file

        count = 0
        print("\nReading '", self.name, "' stock data from: ", self.path)
        if self.log == True:
            loop = tqdm.tqdm(total = len(data), position = 0, leave = False)
        for line in data:
            line = line.split(",")
            # convert all the numbers in the line as integers, create a StockDataPoint
            self.raw.append(float(line[OPEN]))
            self.raw.append(float(line[CLOSE]))
            count += 1
            if self.log == True:
                loop.set_description('Reading stock data...' .format(len(data)))
                loop.update(1)
                time.sleep(0.001)
            else:
                pass
        print("\n\nUploaded stock data successfully!")
    def delete_datapoint(self, index):
        if (index < 0) | (index >= len(self.raw)):
            pass
        else:
            del self.raw[index]
    def datapoint(self, index):
        return self.raw[index]
    def amount_of_datapoints(self):
        return len(self.raw)