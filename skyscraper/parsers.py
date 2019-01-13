import pandas as pd


class TableParser(object):
    def __init__(self, html, header=None):
        self.table = pd.read_html(html, header=header)[0]

    def column(self, col_name):
        return self.table[col_name].tolist()

    def get_dataframe(self):
        return self.table
