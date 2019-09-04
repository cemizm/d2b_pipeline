import pvserve
import pandas as pd
import json
import sys

sm = pvserve.smartmonitoring.Client()
data = sm.getData(3)
dataset = pd.DataFrame(data['list'])
observed_objects = sm.get_observed_objects()

# 5 plant
# 3 dunkel
# 4 hell
# 7 modul
# 6 string

pv_modules = sm.meta_to_file(observed_objects)
sm.curves_to_file(observed_objects, pv_modules)