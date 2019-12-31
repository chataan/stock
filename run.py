#!/usr/bin/env python3

import glob
import googlesearch as googlesearch

model_base = "Models/"

if __name__ == "__main__":
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
        # append the request stock name on request.csv 
        request_form = open("request.csv", "a+")
        request_form.write((query + "\r\n"))
        request_form.close()
    else: # model exists
        print("")
