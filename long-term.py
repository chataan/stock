#!/usr/bin/env python3

from stock import upload
from service import graph, select_model, download_stock, long_term_prediction, git_update
from financial import fetch_last_time_series

if __name__ == "__main__":
    model = select_model()
    print("Model = [", model, "]\n")

    path, id = download_stock()
    st = upload(path, True)
    
    prediction_matrix = long_term_prediction(st, 30, model)
    graph(prediction_matrix, 'red', "long_term_prediction_demo", False)
    
    git_update()
