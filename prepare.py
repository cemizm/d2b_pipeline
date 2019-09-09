import pandas as pd
import os
import matplotlib.pyplot as plt

from pvserve import mlcycle as ml
from pvserve import smartmonitoring as sm
from pvserve import preprocessing as pp

COLS_U = ['Uoc', *sm.SM_CURVE_U]
COLS_I = ['Isc', *sm.SM_CURVE_I]
COLS_ERROR = ["plant_name", "string_name", "Anzahl Module in Serie", "Uoc_meta", "Isc_meta"]

ISC_UOC_TOLERANCE = 1.1

FILTER_IRR = 300

INTERPOLATE_X = 20

print("------------------ Download from MLCycle -------------------")

client_ml = ml.Client()

meta = client_ml.download_dataframe("raw_metadata.csv", index_col=[0, 1])
dark = client_ml.download_dataframe("raw_dark.csv", index_col=[0, 1])
bright = client_ml.download_dataframe("raw_bright.csv", index_col=[0, 1])

dark_count = len(dark.index)
bright_count = len(bright.index)

print("Bright IV-Curves:\t\t{}".format(bright_count))
print("Dark IV-Curves:\t\t\t{}".format(dark_count))

### Prepare data

meta["Uoc_tol"] = meta.Uoc * ISC_UOC_TOLERANCE
meta["Isc_tol"] = meta.Isc * ISC_UOC_TOLERANCE

dark_meta = dark.join(meta, rsuffix="_meta")
bright_meta = bright.join(meta, rsuffix="_meta")

pp.standardize(dark_meta, COLS_U, COLS_I)
pp.standardize(bright_meta, COLS_U, COLS_I)

print("-------------------- Sanity Check Data ---------------------")

drop_bright = pp.check(bright_meta)
drop_dark = pp.check(dark_meta)

drop_dark_len = len(drop_dark[drop_dark == True])
drop_bright_len = len(drop_bright[drop_bright == True])

print("Bright IV-Curve Errors:\t\t{}".format(drop_bright_len))
print("Dark IV-Curves Errors:\t\t{}".format(drop_dark_len))

if drop_bright_len > 0:
    err = pp.group_by_string(bright_meta, drop_bright, COLS_ERROR)

    client_ml.upload_dataframe(err, 'Errors Bright', 'error_bright.csv', 0)

    bright_meta = bright_meta.drop(bright_meta[drop_bright].index)

if drop_dark_len > 0:
    err = pp.group_by_string(dark_meta, drop_dark, COLS_ERROR)

    client_ml.upload_dataframe(err, 'Errors Dark', 'error_dark.csv', 0)
    
    dark_meta = dark_meta.drop(dark_meta[drop_dark].index)

print("---------------------- Filter Data -------------------------")

bfilter = pp.filter(bright_meta, FILTER_IRR)
dfilter = pp.filter_typ(dark_meta)

filter_blen = len(bfilter[bfilter == True])
filter_dlen = len(dfilter[dfilter == True])

if filter_blen > 0:
    print("Low Irr. IV-Curves:\t\t{}".format(filter_blen))
    bright_meta = bright_meta.drop(bright_meta[bfilter].index)

if filter_blen > 0:
    print("Daylight on dark IV-Curves:\t{}".format(filter_dlen))
    dark_meta = dark_meta.drop(dark_meta[dfilter].index)


print("--------------------- Normalize Data -----------------------")

pp.normalize(dark_meta, COLS_U, COLS_I)
pp.normalize(bright_meta, COLS_U, COLS_I)

print("Remaining bright IV-Curves:\t{}".format(bright_meta.shape[0]))
print("Remaining dark IV-Curves:\t{}".format(dark_meta.shape[0]))

fig, ax = plt.subplots(figsize=(18, 10))

ax.scatter(bright_meta['E eff'], 
           (bright_meta['Uoc'] * bright_meta['Isc']))

ax.set_xlabel('Einstrahlung')
ax.set_ylabel('Watt @ Ideal (normalisiert)')

client_ml.upload_plot(fig, "Data Distribution", "dd_bright.png", 0)

fig, ax = plt.subplots(figsize=(18, 10))

ax.scatter(dark_meta['Uoc'], dark_meta['Isc'])

ax.set_xlabel('Uoc (normalisiert)')
ax.set_ylabel('Isc (normalisiert)')

client_ml.upload_plot(fig, "Data Distribution (Dunkel)", "dd_dark.png", 0)

print("---------------------- Interpolation -----------------------")

for index, row in dark_meta.iterrows():
    d = pp.interpolate(row[sm.SM_CURVE_U].values, 
                       row[sm.SM_CURVE_I].values, 
                       INTERPOLATE_X)

    
    

    