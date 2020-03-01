
from datetime import date
from service import download_stock
from stock import upload

class Stock:
    def __init__(self, name, id):
        self.id = id
        self.name = name

        today = date.today()
        today = str(today)
        date_info = today.split("-")
        date_info[0] = str(int(date_info[0]) - 1)
        start_date = ""
        for i in range(len(date_info)):
            if i == len(date_info) - 1:
                today += date_info[i]
            else:
                today += date_info[i] + "-"
        
        csv, i = download_stock(self.id, start_date)
        self.data = upload(csv)

s = Stock('Google', 'goog')