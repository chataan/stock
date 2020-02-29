
from service import download_stock

class Market:
    def __init__(self, list_of_stock_id):
        """ Argument <list_of_stocks> = 'string' list containing a list of stock IDs """
        self.stock_id_list = list_of_stock_id
