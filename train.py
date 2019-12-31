#!/usr/bin/env python3

import stock as stock
import algorithm as algorithm

aapl = "Database/AAPL.csv" # Applc Inc.
goog = "Database/GOOG.csv" # Google Inc.
msft = "Database/MSFT.csv" # Microsoft Inc.
nvda = "Database/NVDA.csv" # NVIDIA Inc.
tsla = "Database/TSLA.csv" # Tesla Inc.

# search given stock query on Google Search Engine 
#query += " finance.yahoo"
#search_result = None
#for link in googlesearch.search(query, tld="co.in", num=1, stop=1, pause=2):
    #search_result = str(link)
# acquire the past year worth of stock data

if __name__ == "__main__":
    google = stock.Stock("Google", goog)
    long_term = algorithm.StockProcessor(google, algorithm.LONG_TERM, 5)
    long_term.run()
    #short_term = algoriht.StockProcessor(google, algorithm.SHORT_TERM, 5)
    #short_term.run()