""" using my sequential forecasting model to rebalance a portfolio """

from service import download_stock
from sequential import sequential_prediction
from sequential import regression_momentum_bias

def generate_portfolio(name, stock_name_list, stock_id_list, stock_balance, stock_shares):
    f = open(name + "_portfolio.txt", "w+")
    for i in range(len(stock_name_list)):
        f.write(stock_id_list[i], " // ", stock_name_list[i], " // ", stock_balance[i], "// ", stock_shares[i])

if __name__ == "__main__":
    stock_id_list = ['']
