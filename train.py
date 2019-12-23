#!/usr/bin/env python3

import stock as stock
import stocklyzer as stocklyzer

if __name__ == "__main__":
    path = "GOOG/train.csv"
    google = stock.Stock(path)
    processor = stocklyzer.StockProcessor(google, stocklyzer.LONG_TERM, 5)
    processor.run()