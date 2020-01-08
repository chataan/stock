#!/usr/bin/env python3

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

from stock import Stock
from algorithm import SHORT_TERM
from algorithm import LONG_TERM
from algorithm import StockProcessor
from model import KerasPredictor

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

long_term_processor = None
short_term_processor = None

if __name__ == "__main__":
    os.system('clear')
    google = Stock("Google", goog, False, True)

    long_term_processor = StockProcessor(google, LONG_TERM, 4)
    long_term_google = KerasPredictor(long_term_processor, "Long_Term_Google_Stock")
    long_term_google.train_model(int(LONG_TERM / 3), 1000, 32)

    short_term_processor = StockProcessor(google, SHORT_TERM, 4)
    short_term_google = KerasPredictor(short_term_processor, "Short_Term_Google_Stock")
    short_term_google.train_model(int(SHORT_TERM / 3), 1000, 32)

    long_term_google.evaluate_test_set()
    short_term_google.evaluate_test_set()
