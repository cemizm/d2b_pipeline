import pvserve
import pandas as pd

sm = pvserve.smartmonitoring.Client()
data = sm.getData(3)
dataset = pd.DataFrame(data['list'])

print(dataset.dtypes)