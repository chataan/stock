#!/usr/bin/env python3

from datetime import date
from service import download_stock, git_update, fetch_last_time_series
from financial import QUARTER
from stock import upload
from prettytable import PrettyTable

class Stock:
    def __init__(self, name, id):
        self.id = id
        self.name = name

        today = date.today()
        today = str(today)
        date_info = today.split("-")
        date_info[0] = str(int(date_info[0]) - 1)
        start_date = ""
        for i in range(len(date_info)):
            if i == len(date_info) - 1:
                today += date_info[i]
            else:
                today += date_info[i] + "-"
        
        csv, i = download_stock(self.id, start_date)
        self.data = upload(csv, 1, True)

        if len(self.data) <= QUARTER:
            self.last_timeseries = None
        else:
            self.last_timeseries = fetch_last_time_series(self.data, QUARTER)
        self.close_price = int(self.data[len(self.data) - 1]) # Korean Stocks should be integers
        self.percentage = 0.00
        self.shares = 0
    def set_rebalance_info(self, percentage, shares):
        self.percentage = float(percentage)
        self.shares = int(shares)
    def stock_name(self):
        return self.name
    def stock_id(self):
        return self.id
    def stock_shares(self):
        return self.shares
    def stock_percentage(self):
        return self.percentage
    def price(self):
        return self.close_price
    def rebalance(self, portfolio_asset, percentage_diff_range):
        """ 1. Calculate how much the stock values in the portfolio (i.e., percentage)
            2. Calculate the difference of the target percentage and actual percentage
                a. if difference > 3.0, return the required amount of purchases/sales
                b. if difference < 3.0, return NONE 
            RETURNS: float<amount of purchases/sales>, sequential prediction matrix 
                          or NONE, sequential prediction matrix """
        evaluate_percentage = self.shares * self.close_price * 100 / portfolio_asset
        percentage_diff = (evaluate_percentage - self.percentage) / self.percentage
        profit = (self.shares * int(self.close_price)) - int((self.percentage * portfolio_asset / 100))
        print(percentage_diff)

class Portfolio:
    def __init__(self, stocks=None, percentage=None, shares=None, d2_asset=0.00):
        self.total_asset = 0.00
        self.d2_asset = d2_asset
        self.stocks = stocks
        if self.stocks != None:
            for i in range(len(stocks)):
                stocks[i].set_rebalance_info(percentages[i], shares[i])
    def display(self):
        table = PrettyTable()
        table.field_names = ['Name', 'ID', 'Rebalance %', 'Shares']
        for s in self.stocks:
            table.add_row([s.stock_name(), s.stock_id(), s.stock_percentage(), s.stock_shares()])
        print(table)
        print('Remaining D2 Cash: {}' .format(self.d2_asset))
        print("TOTAL ASSET = ", self.total_asset)
    def create_portfolio(self, portfolio_name):
        etf_stock_list = open(portfolio_name + "_etf_stock_list.txt", "w+")
        etf_stock_balance = open(portfolio_name + "_etf_balance.txt", "w+")
        for i in range(len(stocks)):
            etf_stock_list.write(stocks[i].stock_name() + ",")
            etf_stock_list.write(stocks[i].stock_id() + ",")
            etf_stock_balance.write(str(stocks[i].stock_percentage()) + ",")
            etf_stock_balance.write(str(stocks[i].stock_shares()) + ",")
        etf_stock_balance.write(str(self.d2_asset))
        etf_stock_list.close()
        etf_stock_balance.close()
    def load(self, portfolio_name):
        self.d2_asset, self.stocks = 0, []
        # read stock list, balance (i.e., percentages), shares, and assets
        try:
            etf_stock_list = open(portfolio_name + "_etf_stock_list.txt", "r")
            etf_stock_balance = open(portfolio_name + "_etf_balance.txt", "r")
            stock_list = etf_stock_list.read().split(",")
            stock_balance = etf_stock_balance.read().split(",")

            for i in range(0, len(stock_list) - 2, 2):
                self.stocks.append(Stock(stock_list[i], stock_list[i + 1])) # stock name, stock ID
                self.stocks[len(self.stocks) - 1].set_rebalance_info(stock_balance[i], stock_balance[i + 1]) # stock balance %, shares
                self.total_asset += int(self.stocks[len(self.stocks) - 1].price()) * self.stocks[len(self.stocks) - 1].stock_shares()
            self.d2_asset = int(stock_balance[len(stock_balance) - 1])
            self.total_asset += self.d2_asset
            #### UPDATE THE AMOUNT OF SHARES THROUGH USER INPUT ###
        except IOError:
            print("Cannot find ETF info named, '{}'" .format(portfolio_name))
    def deposit(self, value):
        self.d2_asset += value
    def rebalance(self):
        """ Display rebalancing information for the day """
        for s in self.stocks:
            s.rebalance(self.total_asset, 3.3)

# create ETF portfolio using this module
if __name__ == "__main__":
    latin = Stock('TIGER Latin 35', '105010.KS')
    government_bond3 = Stock('Government Bond 3 Years', '114260.KS')
    gold = Stock('Gold', '132030.KS')
    s_and_p = Stock('S&P 500', '143850.KS')
    government_bond10 = Stock('Government Bond 3 Years', '148070.KS')
    china_a50 = Stock("KODEX China A50", '169950.KS')
    vietnam_vn30 = Stock("KINDEX Vietnam VN30", '245710.KS')
    russia_msci = Stock("Russias MSCI", '265690.KS')
    volatility = Stock("KODEX Volatility", '279540.KS')
    usa_bond30 = Stock('USA Bond 30 years', '304660.KS')
    battery = Stock("TIGER Secondary Battery", '305540.KS')
    ultra_government_bond = Stock("HANARO KAP Government Bond", '346000.KS')

    stocks = [gold, china_a50, vietnam_vn30, volatility, battery, s_and_p, latin, russia_msci, usa_bond30, ultra_government_bond, government_bond10, government_bond3]
    percentages = [8, 8, 8, 8, 8, 4, 2, 2, 12, 12, 16, 10]
    shares = [78, 56, 85, 112, 131, 19, 149, 17, 88, 23, 13, 18]

    etf = Portfolio(stocks, percentages, shares, 801033)
    etf.create_portfolio("junyoung")
    git_update()