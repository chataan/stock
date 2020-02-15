#!/usr/bin/env python3

from stock import upload
from service import select_model, download_stock, run, git_update

if __name__ == "__main__":
    while True:
        model = select_model()
        print("Model = [", model, "]\n")

        path, id = download_stock()
        st = upload(path, True)

        raw_prediction = run(st, model)
        print(raw_prediction, "\n")
        git_update()
        print("\n\n\n")