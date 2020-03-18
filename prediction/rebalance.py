#!/usr/bin/env python3

# using my sequential forecasting model to rebalance a portfolio
# run this module by typing: ./forecast-rebalancing.py

# 1. create a portfolio using generate_portfolio()

from os import system
from datetime import date
from service import git_update
from service import download_stock
from service import fetch_last_time_series
from financial import QUARTER
from sequential import sequential_prediction
from sequential import regression_momentum_bias

def load_portfolio(name):
    cash = 0
    stock_name_list, stock_id_list, stock_balance, stock_shares = [], [], [], []
    try:
        f = open(name + "_portfolio.ptf", "r")
        info = f.readlines()
        for line in info:
            line = line.split(" || ")
            if len(line) != 1:
                stock_id_list.append(line[0])
                stock_name_list.append(line[1])
                stock_balance.append(float(line[2]))
                stock_shares.append(int(line[3].strip("\n")))
            else: # cash info
                cash = int(line[0])
    except IOError:
        print("Failed to find portfolio named '", name, "'")
    return stock_id_list, stock_name_list, stock_balance, stock_shares, cash

def write_portfolio(name, stock_name_list, stock_id_list, stock_balance, stock_shares, cash):
    f = open(name + "_portfolio.ptf", "w+")
    for i in range(len(stock_name_list)):
        info = stock_id_list[i] + " || " + stock_name_list[i] + " || " + str(stock_balance[i]) + " || " + str(stock_shares[i]) + "\n"
        f.write(info)
    f.write(str(cash))
    f.close()

# initial portfolio information (2020.03.16)
stock_id_list = ['132030.KS', '169950.KS', '245710.KS', '279540.KS', '305540.KS', '143850.KS', '105010.KS', '265690.KS', '304660.KS', '148070.KS', '167860.KS', '267490.KS']
stock_name_list = ['Gold', 'China A50', 'Vietnam VN30', 'KODEX Votality', 'Secondary Battery', 'S&P 500', 'Latin', 'Russia', 'US Ultra 30 yrs', 'Korea 10 yrs', 'Korea 10 yrs Leverage', 'KBSTAR US Long Term Leverage']
stock_balance = [8.0, 7.6, 7.7, 7.6, 7.7, 7.8, 4.5, 3.7, 10.0, 10.0, 10.0, 10.0]
stock_shares = [96, 59, 96, 131, 157, 36, 248, 23, 100, 13, 8, 90]
cash = 804928

# un-comment the below only when desired to create an initial portfolio
write_portfolio('junyoung', stock_name_list, stock_id_list, stock_balance, stock_shares, cash)

system('clear')
if __name__ == "__main__":
    dataset = [] # used as an array for containing time series data of stocks for forecasting
    price, evaluated_value, evaluated_percentage, percentage_difference, profit = [], [], [], [], []
    stock_id_list, stock_name_list, stock_balance, stock_shares, cash = load_portfolio('junyoung')

    total_stock_balance = 0
    for val in stock_balance:
        total_stock_balance += val

    # get date YYYY-MM-DD string 1 year before
    start_date = ""
    today = str(date.today())
    date_info = today.split("-")
    date_info[0] = str(int(date_info[0]) - 1)
    for i in range(len(date_info)):
        if i == len(date_info) - 1:
            start_date += date_info[i]
        else:
            start_date += date_info[i] + "-"

    print("Downloading/uploading historcial stock data from finance.yahoo.com....")
    # download historical data, get one time series from stock, get close price
    for id in stock_id_list:
        historical, id = download_stock(id, start_date, 1, False)
        timeseries, close_price = fetch_last_time_series(historical, QUARTER)
        dataset.append(timeseries)
        price.append(int(close_price))

    cash_balance = 100.0 - total_stock_balance
    adjustment_value = 0.3 # THIS VALUE COULD BE TUNED

    # run sequential prediction before rebalancing
    predictions = []
    print("Running prediction models... ")
    for i in range(len(dataset)):
        stock, prediction = sequential_prediction(model=stock_id_list[i].lower(), stock_id=stock_id_list[i].lower(), date=start_date, log=False, bias_type='REGRESSION', itr=10)
        if prediction == []: # meaning that no model exists
            predictions.append('NO MODEL')
        else:
            # predicted growth
            if prediction[len(prediction) - 1] > stock[len(stock) - 1]:
                predictions.append('POSITIVE')
            else:
                predictions.append('NEGATIVE')
    
    # based on the prediction output, tune all the stock balances
    # if prediction is POSITIVE, take <adjustment_value> from <cash_balance> to the stock
    # if prediction is NEGATIVE, take <adjustment_value> from stock to <cash_balance>
    for i in range(len(predictions)):
        if predictions[i] == 'POSITIVE':
            cash_balance -= adjustment_value
            stock_balance[i] += adjustment_value
        else:
            cash_balance += adjustment_value
            stock_balance[i] -= adjustment_value
    print(stock_balance, "\n")

    # run rebalancing calculations

    git_update()