#!/usr/bin/env python3

import os
from stock import upload
from service import graph, select_model, download_stock, sequential_prediction, git_update
from financial import fetch_last_time_series

if __name__ == "__main__":
    while True:
        model = select_model()
        print("Model = [", model, "]\n")

        path, id = download_stock()
        st = upload(path, True)
    
        prediction_matrix = sequential_prediction(st, 10, model)
        print(prediction_matrix)
        graph_title = model + "_sequential_prediction_demo"
        graph(prediction_matrix, 'red', graph_title, False)
    
        git_update()
        os.system('clear')
