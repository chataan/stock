#!/usr/bin/env python3

from stock import upload
from service import download_stock, git_update
from financial import partition_time_series, n_shape_analysis

if __name__ == "__main__":
    csv, id = download_stock()
    stock = upload(csv)
    n_shape_analysis(stock)