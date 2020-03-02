
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
        change = ((total_asset - previous_asset) / total_asset) * 100
        for i in range(_range, _range - evaluate_range, -1):
            if stock[_range] > stock[i]:
                momentum += 1
        if momentum != 0:
            stock_asset = int(total_asset * (momentum / evaluate_range))
            shares = int(stock_asset / stock[_range])
            cash = total_asset - stock_asset
        previous_asset = total_asset
        print("Total = ", total_asset, " [ Stock = ", stock_asset, ", Cash = ", cash, "] --> Shares: ", shares, ", < CHANGE=", change, ">")
    print(stock[0])