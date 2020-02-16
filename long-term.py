#!/usr/bin/env python3

from stock import upload
from service import select_model, download_stock, git_update
from financial import fetch_last_time_series

if __name__ == "__main__":
    model = select_model()
    print("Model = [", model, "]\n")

    path, id = download_stock()
    st = upload(path, True)
    timeseries = fetch_last_time_series(st, 90)

    print(timeseries)
    git_update()
