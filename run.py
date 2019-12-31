#!/usr/bin/env python3

import glob
import googlesearch as googlesearch

model_base = "Models/"

# search given stock query on Google Search Engine 
#query += " finance.yahoo"
#search_result = None
#for link in googlesearch.search(query, tld="co.in", num=1, stop=1, pause=2):
    #search_result = str(link)
# acquire the past year worth of stock data

if __name__ == "__main__":
    print("")
    query = input("Search a stock: ")
    query = query.lower()
    # check if there is an existing prediction model on the given stock
    i = 0
    model_path = None
    models = [f for f in glob.glob((model_base + "**/*.h5"), recursive=True)]
    for model in models:
        if (query in model) == True:
            model_path = model
            break
        else:
            pass
    if model_path == None: # no model exists for the requested stock
        print("\nThere were no models that matched your stock search query!")
        print("A model training request will be written for the following stock!\n")
        # append the request stock name on request.csv 
        request_form = open("request.csv", "a+")
        request_form.write((query + "\r\n"))
        print("\nRequest submitted!\n")
        request_form.close()
    else: # model exists
        print("")
