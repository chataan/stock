#!/usr/bin/env python3

import stock as stock
import preprocessing as stockprocessor

if __name__ == "__main__":
    path = "../GOOG/train.csv"
    google = stock.Stock(path)
    processor = stockprocessor.StockProcessor(google, 30, 5)
    processor.run()