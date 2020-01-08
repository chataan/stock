#!/usr/bin/env python3

import glob
import googlesearch as googlesearch
from stock import Stock
from algorithm import StockProcessor
from algorithm import LONG_TERM, SHORT_TERM
from model import KerasPredictor

model_base = "Models/"

# search given stock query on Google Search Engine 
#query += " finance.yahoo"
#search_result = None
#for link in googlesearch.search(query, tld="co.in", num=1, stop=1, pause=2):
    #search_result = str(link)
# acquire the past year worth of stock data

if __name__ == "__main__":
    """ REQUIREMENTS TO USE THE PREDICTOR """
    """ To use the predictor, you need the following information: 
        1. Stock (Upload .csv)
        2. StockProcessor (process the uploaded stock) 
        3. KerasPredictor
            a. load a model
            b. run """
    predictor = KerasPredictor()
    google = Stock("Google", "Database/GOOG_PREDICT.csv", False, True)
    predictor.load("short_term_google")
    predictor.run(google, SHORT_TERM, 4)
