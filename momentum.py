#!/usr/bin/env python3

from service import download_stock, git_update
from stock import upload
from invest import momentum_investing


if __name__ == "__main__":
    csv, id = download_stock()
    stock = upload(csv, 5, True)
    momentum_investing(stock, 100000000, 12, 5)
    git_update()
