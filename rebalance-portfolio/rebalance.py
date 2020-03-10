#!/usr/bin/env python3

import os
from service import git_update
from portfolio import Portfolio

os.system('clear')

if __name__ == "__main__":
    portfolio = Portfolio()
    portfolio.load("junyoung")
    portfolio.display()
    portfolio.rebalance()
    git_update()
    