#!/usr/bin/env python3

import os
from stock import upload
from service import select_model, download_stock, git_update
from financial import fetch_last_time_series

if __name__ == "__main__":
	
