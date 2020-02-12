#!/usr/bin/env python3

from stock import upload
from service import download_stock, git_update
from financial import partition_time_series, average_growth

if __name__ == "__main__":
    csv, id = download_stock()
    stock = upload(csv)
    dataset = partition_time_series(stock, 35, 0)
    print(average_growth(dataset))
    git_update()