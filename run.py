#!/usr/bin/env python3

from stock import upload
from service import select_model, download_stock, run

if __name__ == "__main__":
    model = select_model()
    print("Model = [", model, "]\n")

    path, id = download_stock()
    st = upload(path, True)

    run(st, model)