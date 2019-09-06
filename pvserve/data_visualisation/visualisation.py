import pvserve
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


class Visualisation:
    
    def plot_graph(self, dataset, type):
        prep_data = pvserve.smartmonitoring.PrepareData()
        if type == "dark":
            prefix = "dark_"
        elif type == "bright":
            prefix = "bright_"
        columns = []
        for column in dataset.columns.values:
            if prefix in column and not "max_x" in column:
                columns.append(column)
        
        for index, row in dataset.iterrows():
            y = []
            for value in row[columns]:
                y.append(value)
            if not (prefix + "max_x") in row:
                max_x = 1
            else:
                max_x = row[prefix + "max_x"]
            x = prep_data.calculate_scala(len(y), max_x)
            
            df = pd.DataFrame({'x':x, 'y':y})
            df = df.sort_values('x')
            df.plot('x', 'y', kind='scatter')
            plt.show()
