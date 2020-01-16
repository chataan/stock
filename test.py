#!/usr/bin/env python3

from yahoo_finance import Share

google = Share('GOOG')
data = google.get_historical('2005-08-31', '2020-01-16')

print(type(data))
