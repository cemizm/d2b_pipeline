import pandas as pd
import pvserve
import sys

prep_data = pvserve.smartmonitoring.PrepareData()

meta_file = "res/meta_data.csv"
meta_data = pd.read_csv(meta_file)

bright_file = "res/bright_curves.csv"
bright_curves = pd.read_csv(bright_file)
bright_curves = prep_data.cut_curves(bright_curves)

dark_file = "res/dark_curves.csv"
dark_curves = pd.read_csv(dark_file)

dark_x_bright = pd.merge(bright_curves, dark_curves, how="inner", on='parent_id')
dark_x_bright.to_csv("res/dark_x_bright.csv")
xxxx = pd.merge(dark_x_bright, meta_data, left_on='parent_id', right_on='string_id')
xxxx.to_csv("res/xxxx.csv")

columns=["plant_id","string_id","temp", "E eff","Isc","Uoc","dark_max_x", "bright_max_x","dark_0","dark_1","dark_2","dark_3","dark_4",
    "dark_5","dark_6","dark_7","dark_8","dark_9","dark_10","dark_11","dark_12",
    "dark_13","dark_14","bright_0","bright_1","bright_2","bright_3","bright_4",
    "bright_5","bright_6","bright_7","bright_8","bright_9","bright_10","bright_11","bright_12",
    "bright_13","bright_14"]

dataframe = pd.DataFrame(columns=columns)

for index, row in xxxx.iterrows():
    bright_x, bright_y = prep_data.get_x_y_data(row, "_x")
    dark_x, dark_y = prep_data.get_x_y_data(row, "_y")
    if len(bright_x) > 10 and len(dark_x) > 10:
        bright_scala, bright_y = prep_data.get_interpolated_data_arrays(bright_x, bright_y, 15)
        dark_scala, dark_y = prep_data.get_interpolated_data_arrays(dark_x, dark_y, 15)
        dict = {
            "plant_id" : row["plant_id"],
            "string_id" : row["string_id"],
            "temp" : row["T mod"],
            "E eff" : row["E eff"],
            "Isc" : row["Isc 0"],
            "Uoc" : row["Uoc 0"],
            "dark_max_x" : dark_x[-1],
            "bright_max_x" : bright_x[-1],
            "dark_0" : dark_y[0],
            "dark_1" : dark_y[1],
            "dark_2" : dark_y[2],
            "dark_3" : dark_y[3],
            "dark_4" : dark_y[4],
            "dark_5" : dark_y[5],
            "dark_6" : dark_y[6],
            "dark_7" : dark_y[7],
            "dark_8" : dark_y[8],
            "dark_9" : dark_y[9],
            "dark_10" : dark_y[10],
            "dark_11" : dark_y[11],
            "dark_12" : dark_y[12],
            "dark_13" : dark_y[13],
            "dark_14" : dark_y[14],
            "bright_0" : bright_y[0],
            "bright_1" : bright_y[1],
            "bright_2" : bright_y[2],
            "bright_3" : bright_y[3],
            "bright_4" : bright_y[4],
            "bright_5" : bright_y[5],
            "bright_6" : bright_y[6],
            "bright_7" : bright_y[7],
            "bright_8" : bright_y[8],
            "bright_9" : bright_y[9],
            "bright_10" : bright_y[10],
            "bright_11" : bright_y[11],
            "bright_12" : bright_y[12],
            "bright_13" : bright_y[13],
            "bright_14" : bright_y[14],
        }
        dataframe = dataframe.append(dict, ignore_index=True)

dataframe.to_csv("res/trainingsdata.csv")


'''
Trainingsdaten:
    15 I Werte der Dunkelkennlinie
    Temp der Ziel Hellkennlinie
    Einstrahlungsstärke der Ziel Hellkennlinie

Zieldaten:
    15 I Werte der Hellkennlinie
    Isc kurzschlussstrom
    Uoc leerlaufspannung

'''