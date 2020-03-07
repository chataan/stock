#!/usr/bin/env python3

import service
import stock
import financial
from os import system
from time import sleep

print("Running experimental environment...")
sleep(2)
system('clear')

if __name__ == "__main__":
    model = service.select_model()
    print("Model = [", model, "]\n")

    csv, id, date = service.download_stock()
    st = stock.upload(csv, True)

    service.visualize_model_prediction(st, model, date)