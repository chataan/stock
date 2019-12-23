
import time as time
import tqdm as tqdm

YEAR=0
MONTH=1
DATE=2
OPEN=3
CLOSE=7

class StockDataPoint:
    def __init__(self, year, month, date, value):
        self.year = year
        self.month = month
        self.date = date
        self.value = value
    def date(self):
        return self.year, self.month, self.date
    def price(self):
        return self.value
    def edit_value(self, val):
        self.value = val

class Stock:
    def __init__(self, path):
        self.path = path
        self.datapoints = self.upload_stock_data()
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
        print("\nReading stock data from: ", self.path)
        loop = tqdm.tqdm(total = len(data), position = 0, leave = False)
        for line in data:
            line = line.split(",")
            # convert all the numbers in the line as integers, create a StockDataPoint
            uploaded.append(StockDataPoint(int(line[YEAR]), int(line[MONTH]), int(line[DATE]), float(line[OPEN])))
            uploaded.append(StockDataPoint(int(line[YEAR]), int(line[MONTH]), int(line[DATE]), float(line[CLOSE])))
            count += 1
            loop.set_description('Reading stock data...' .format(len(data)))
            loop.update(1)
            time.sleep(0.01)
        print("\n\nUploaded stock data successfully!")
        return uploaded
    def delete_datapoint(self, index):
        if (index < 0) | (index >= len(self.datapoints)):
            pass
        else:
            del self.datapoints[index]
    def datapoint(self, index):
        return self.datapoints[index]
    def amount_of_datapoints(self):
        return len(self.datapoints)