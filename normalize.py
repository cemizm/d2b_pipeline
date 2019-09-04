import pandas as pd
import pvserve
import sys

MAX_TEMPERATURE = 100
MAX_SOLARRADIATION = 1367
ISC_CONSTANT = 2
UOC_CONSTANT = 70
DARK_CONSTANT = -2
print_columns = ["Isc", "Uoc", "dark_0", "dark_13", "dark_14", "bright_0", "bright_14"]

trainings_file = "res/trainingsdata.csv"
trainings_data = pd.read_csv(trainings_file)

print(trainings_data.head())

trainings_data['temp'] = trainings_data['temp'] / MAX_TEMPERATURE
trainings_data['E eff'] = trainings_data['E eff'] / MAX_SOLARRADIATION

for i in range(0,15):
    column_bright = "bright_" + str(i)
    trainings_data[column_bright] = trainings_data[column_bright] / trainings_data["Isc"]
    column_dark = "dark_" + str(i)
    trainings_data[column_dark] = trainings_data[column_dark] / DARK_CONSTANT

trainings_data['temp'] = trainings_data['temp'] / MAX_TEMPERATURE
trainings_data['E eff'] = trainings_data['E eff'] / MAX_SOLARRADIATION

print(trainings_data[print_columns].head())

trainings_data.to_csv("res/normalized_trainingsdata.csv")