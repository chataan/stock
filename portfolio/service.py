
import os
import time
import tqdm
import matplotlib.pyplot as plt
from pandas_datareader.data import DataReader

YEAR=0
MONTH=1
DATE=2
OPEN=3
CLOSE=6

def git_update():
    os.system("git remote set-url origin git@github.com:junyoung-sim/stock")
    os.system("git add -A")
    os.system("git commit -am 'Automated Commision'")
    os.system("git push")
def graph(matrix, _color, save_name, show=False):
    count = []
    for i in range(len(matrix)):
        count.append(i)
    plt.plot(count, matrix, color=_color)
    plt.xlabel("Count")
    plt.ylabel("Value")
    if show != False:
        plt.show()
    plt.savefig(save_name)
def download_stock(stock_id="", start_date="", period=1, log=True):
    """ stock_id --> ex: AAPL (str)
        start_date --> ex: 2020-01-19 (str) """
    if (stock_id == "") & (start_date == ""):
        stock_id = input("Enter stock ID (ex: AAPL) = ")
        start_date = input("Enter start date (ex: 2020-01-19) = ")
    else:
        pass
    stock = DataReader(stock_id, "yahoo", start_date)
    csv = "../Database/" + stock_id + ".csv"
    stock.to_csv(csv)

    uploaded = []
    data = []
    file = open(csv, "r")
    info = file.readlines()
    for x in info:
        data.append(x)
        data[len(data) - 1] = data[len(data) - 1].replace("-", ",")
    del data[0] # delete the line: "Date,Open,High,Low,Close,Adj Close,Volume" on the .csv file

    raw = []
    count = 0
    print("\nReading stock data from [", csv, "]")
    if log == True:
        loop = tqdm.tqdm(total = int(len(data) / period), position = 0, leave = False)
    for i in range(0, len(data), period):
        line = data[i].split(",")
        raw.append(float(line[CLOSE]))
        count += 1
        if log == True:
            loop.set_description('Reading stock data...' .format(len(data)))
            loop.update(1)
            time.sleep(0.001)
        else:
            pass
    print("\n\nUploaded stock data successfully!")

    return raw, stock_id
