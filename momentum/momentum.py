#!/usr/bin/env python3

from service import download_stock, git_update
from stock import upload

def momentum_investing(stock, principal, evaluate_range, evaluate_period):
    """ principal = 원금, evaluate_range = n주 전 데이터 반영, 
        evaluate_period = 평가 주기 """
    cash = principal
    shares = 0
    stock_asset = 0
    total_asset = principal
    previous_asset = 0
    for _range in range(evaluate_range, len(stock) - evaluate_range, evaluate_period):
        momentum = 0
        total_asset = int(cash + (stock[_range] * shares))
        change = ((total_asset - principal) / principal) * 100
        bh_change = (stock[_range] - stock[evaluate_range]) * 100 / stock[evaluate_range]
        for i in range(_range, _range - evaluate_range, -1):
            if stock[_range] > stock[i]:
                momentum += 1
        stock_asset = int(total_asset * (momentum / evaluate_range))
        shares = int(stock_asset / stock[_range])
        cash = total_asset - shares * stock[_range]
        previous_asset = total_asset
        print("Total = ", total_asset, " [ Stock = ", stock_asset, ", Cash = ", cash, "] --> Shares: ", shares, ", < CHANGE=", change, ">", "<BH Change = ", bh_change, ">", stock[_range])
    print("Final Profit = ", (total_asset - principal) * 100 / principal)
    print(stock[0])

if __name__ == "__main__":
    csv, id = download_stock()
    stock = upload(csv, 5, True)
    momentum_investing(stock, 100000000, 12, 5)
    git_update()