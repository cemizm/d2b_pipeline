import pvserve
import pandas as pd
import os

class Client:
    def __init__(self):
        filepath = "pvserve/moduldb/modul_daten.xlsx"
        self.df = pd.read_excel(filepath)

    def get_modul_data(self, modultyp):
        row = self.df[self.df.Modultyp == modultyp]
        if len(row) == 0:
            return None

        return row.to_dict()
