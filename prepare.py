import pandas as pd
import os
import matplotlib.pyplot as plt

from pvserve import mlcycle as ml
from pvserve import smartmonitoring as sm

COLS_U = ['Uoc', *sm.SM_CURVE_U]
COLS_I = ['Isc', *sm.SM_CURVE_I]
COLS_ERROR = ["plant_name", "string_name", "Anzahl Module in Serie", "Uoc_meta", "Isc_meta"]

ISC_UOC_TOLERANCE = 1.1

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

print("-------------------- Sanity Check Data ---------------------")

dark_meta[COLS_U] = dark_meta[COLS_U].divide(dark_meta["Anzahl Module in Serie"], axis="index")
bright_meta[COLS_U] = bright_meta[COLS_U].divide(bright_meta["Anzahl Module in Serie"], axis="index")

berror = bright_meta.Uoc_meta.isnull() 
berror = berror | bright_meta.Isc_meta.isnull()
berror = berror | (bright_meta.Uoc > bright_meta.Uoc_tol) 
berror = berror | (bright_meta.Isc > bright_meta.Isc_tol)
berror = berror | (bright_meta.Uoc < 0)
berror = berror | (bright_meta.Isc < 0)

drop_bright = berror

berror = bright_meta[berror][COLS_ERROR]
berror = berror.reset_index().drop(columns='data_id')
berror = berror.drop_duplicates().reset_index(drop=True)

derror = dark_meta.Uoc_meta.isnull() 
derror = derror | dark_meta.Isc_meta.isnull()
derror = derror | (dark_meta.Uoc > dark_meta.Uoc_tol)
derror = derror | (dark_meta.Isc > dark_meta.Isc_tol)

drop_dark = derror

derror = dark_meta[derror][COLS_ERROR]
derror = derror.reset_index().drop(columns='data_id')
derror = derror.drop_duplicates().reset_index(drop=True)

drop_dark_len = len(drop_dark[drop_dark == True])
drop_bright_len = len(drop_bright[drop_bright == True])


if drop_bright_len > 0:
    print("Bright IV-Curve Errors:\t\t{}".format(drop_bright_len))
    client_ml.upload_dataframe(berror, 'Errors Bright', 'error_bright.csv', 0)

    bright_meta = bright_meta.drop(bright_meta[drop_bright].index)

if drop_dark_len > 0:
    print("Dark IV-Curves Errors:\t\t{}".format(drop_dark_len))
    client_ml.upload_dataframe(berror, 'Errors Dark', 'error_dark.csv', 0)
    
    dark_meta = dark_meta.drop(dark_meta[drop_dark].index)

print("--------------------- Normalize Data -----------------------")

dark_meta[COLS_U] = dark_meta[COLS_U].divide(dark_meta.Uoc_tol, axis="index")
dark_meta[COLS_I] = dark_meta[COLS_I].divide(dark_meta.Isc_tol, axis="index")

bright_meta[COLS_U] = bright_meta[COLS_U].divide(bright_meta.Uoc_tol, axis="index")
bright_meta[COLS_I] = bright_meta[COLS_I].divide(bright_meta.Isc_tol, axis="index")

fig, ax = plt.subplots(figsize=(18, 10))

ax.scatter(bright_meta['E eff'], 
           (bright_meta['Uoc'] * bright_meta['Isc']))

ax.set_xlabel('Einstrahlung')
ax.set_ylabel('Watt @ MPP (normalisiert)')

client_ml.upload_plot(fig, "Data Distribution", "dd_bright.png", 0)

fig, ax = plt.subplots(figsize=(18, 10))

ax.scatter(bright_meta['Uoc'], bright_meta['Isc'])

ax.set_xlabel('Uoc (normalisiert)')
ax.set_ylabel('Isc (normalisiert)')

client_ml.upload_plot(fig, "Data Distribution (Dunkel)", "dd_dark.png", 0)