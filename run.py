#!/usr/bin/env python3

import googlesearch as googlesearch

if __name__ == "__main__":
    query = input("Search a stock: ")
    # check if there is an existing prediction model on the given stock
    # search given stock query on Google Search Engine 
    query += " finance.yahoo"
    search_result = None
    for link in googlesearch.search(query, tld="co.in", num=1, stop=1, pause=2):
        search_result = str(link)
    # acquire the past year worth of stock data 