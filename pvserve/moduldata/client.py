import pvserve
import pandas as pd
import os

class Client:

    def get_modul_data(self):
        filepath = "pvserve/moduldata/modul_daten.xlsx"
        df = pd.read_excel(filepath)
        return df
