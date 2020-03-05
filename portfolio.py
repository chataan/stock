
from datetime import date
from service import download_stock
from stock import upload

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

        self.data = upload(csv)
        self.last_timeseries = None
        self.close_price = self.data[len(self.data) - 1]
        self.percentage = 0.00
        self.shares = 0
    def set_rebalance_info(self, percentage, shares):
        self.percentage = percentage
        self.shares = shares

class Portfolio:
    def __init__(self, stocks, percentages, shares, d_2_asset):
        self.d2_asset = d2_asset
        self.stocks = stocks
        for i in range(len(stocks)):
            stocks.set_rebalance_info(percentages[i], shares[i])
            
# create ETF portfolio using this module

latin = Stock('TIGER Latin 35', '')
government_bond3 = Stock('Government Bond 3 Years', '')
gold = Stock('Gold', '')
s_and_p = Stock('S&P 500', '^gspc')
government_bond10 = Stock('Government Bond 3 Years', '')
china_a50 = Stock("KODEX China A50", '')
vietnam_vn30 = Stock("KINDEX Vietnam VN30", '')
russia_msci = Stock("Russias MSCI", '')
volatility = Stock("KODEX Volatility", '')
usa_bond30 = Stock('USA Bond 30 years', '')
battery = Stock("TIGER Secondary Battery", '')
ultra_government_bond = Stock("HANARO KAP Government Bond", '')

stocks = [latin, government_bond3, gold, s_and_p, government_bond10, china_a50, russia_msci, volatility, usa_bond30, battery, ultra_government_bond]
percentages = [1.0, 10.0, 8.0, 4.0, 16.0, 8.0, 2.0, 8.0, 12.0, 8.0, 12.0]
