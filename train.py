#!/usr/bin/env python3

import stock as stock
import algorithm as algorithm

if __name__ == "__main__":
    path = "GOOG/train.csv"
    google = stock.Stock("Google", path)
    long_term = algorithm.StockProcessor(google, algorithm.LONG_TERM, 5)
    #short_term = algoriht.StockProcessor(google, algorithm.SHORT_TERM, 5)
    long_term.run()
    #short_term.run()