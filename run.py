#!/usr/bin/env python3

from stock import upload
from service import select_model, run

if __name__ == "__main__":
    model = select_model()
    print("Model = [", model, "]\n")

    stock_path = input("Enter path to stock: ")
    st = upload(stock_path, True)

    run(st, model)