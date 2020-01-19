#!/usr/bin/env python3

from pandas_datareader import data
from datetime import datetime

aapl = data.DataReader("AAPL", "yahoo", datetime("1908-01-01"))
aapl.to_csv('Database/appl.csv')

