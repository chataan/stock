#!/usr/bin/env python3

import os
from datetime import date
from service import download_stock, git_update
from prettytable import PrettyTable

class Stock:
    def __init__(self, name, id):
        self.id = id
        self.name = name
        self.start_date = ""
        self.data = None
        self.close_price = 0
        self.percentage = 0.00
        self.shares = 0
        self.required_purchase_sales = 0.00
        self.percentage_diff = 0

        today = date.today()
        today = str(today)
        date_info = today.split("-")
        date_info[0] = str(int(date_info[0]) - 1)
        for i in range(len(date_info)):
            if i == len(date_info) - 1:
                self.start_date += date_info[i]
            else:
                self.start_date += date_info[i] + "-"
        
        self.data, _ = download_stock(self.id, self.start_date, 1, True)
        self.close_price = self.data[len(self.data) - 1]
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
    def prediction_result(self):
        return self.prediction
    def purchase_sales(self):
        return self.required_purchase_sales
    def percentage_difference(self):
        return self.percentage_diff
    def rebalance(self, portfolio_asset):
        """ 1. Calculate how much the stock values in the portfolio (i.e., percentage)
            2. Calculate the difference of the target percentage and actual percentage
                a. if difference > 3.0, return the required amount of purchases/sales
                b. if difference < 3.0, return NONE 
            RETURNS: float<amount of purchases/sales>, sequential prediction matrix 
                          or NONE, sequential prediction matrix """
        actual_percentage = self.shares * self.close_price / portfolio_asset * 100
        self.percentage_diff = (actual_percentage - self.percentage) * 100 / self.percentage
        profit = (self.shares * self.close_price) - (self.percentage * portfolio_asset / 100)
        self.required_purchase_sales = profit / self.close_price

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
        print("\n", table)
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
        rebalance_table = PrettyTable()
        rebalance_table.field_names = ['Name', 'ID', 'Price', 'Percentage Diff', 'Required Purchase/Sales', 'Status']
        for s in self.stocks:
            status = None
            s.rebalance(self.total_asset)
            if (abs(s.percentage_difference()) > 3.8) & (abs(s.purchase_sales()) > 1.0):
                status = "ACT"
            else:
                status = ""
            rebalance_table.add_row([s.stock_name(), s.stock_id(), s.price(), s.percentage_difference(), s.purchase_sales(), status])
        check = input("Click any key to view rebalance information...")
        os.system("clear")
        print("Rebalancing Information:")
        print(rebalance_table)

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
    percentages = [7.5, 8.0, 8.0, 8.0, 8.0, 6.0, 3.5, 3.5, 10.0, 10.0, 12.0, 8.4]
    shares = [78, 54, 87, 117, 138, 27, 152, 18, 86, 23, 11, 18]

    etf = Portfolio(stocks, percentages, shares, 849015)
    etf.create_portfolio("junyoung")
    git_update()