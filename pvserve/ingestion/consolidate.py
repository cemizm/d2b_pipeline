import pandas as pd
import numpy as np

SM_CURVE_I = ["I" + str(i) for i in range(1, 251)]
SM_CURVE_U = ["U" + str(i) for i in range(1, 251)]

def consolidate_bright(bright, meta):
    df_c = bright[['T mod', 'E eff', 'Isc', 'Uoc', 'Ipmax', 'Upmax']]
    df_ds = meta[['Isc', 'Uoc', 'Impp', 'Umpp']]
    df_m = meta[['plant_name', 'string_name', 'Anzahl Module in Serie', 'Modulhersteller', 'Modultyp']]
    df_u = bright[SM_CURVE_U]
    df_i = bright[SM_CURVE_I]

    df_c.columns = pd.MultiIndex.from_arrays([['Env', 'Env', 'Char', 'Char', 'Char', 'Char'], ['Temp', 'Irr', 'Isc', 'Uoc', 'Impp', 'Umpp']])
    df_ds.columns = pd.MultiIndex.from_product([['STC'], df_ds.columns])
    df_m.columns = pd.MultiIndex.from_product([['Meta'], ['plant_name', 'string_name', 'in_serie', 'hersteller', 'modultyp']])

    df_u.columns = pd.MultiIndex.from_product([['U'], range(1, 251)])
    df_i.columns = pd.MultiIndex.from_product([['I'], range(1, 251)])

    df_ds = df_c.join(df_ds)
    df_ds = df_ds.join(df_m)

    df_iv = df_u.join(df_i)

    return df_ds.join(df_iv, how='right')

def consolidate_dark(dark, meta):
    df_ds = meta[['Isc', 'Uoc', 'Impp', 'Umpp']]
    df_m = meta[['plant_name', 'string_name', 'Anzahl Module in Serie', 'Modulhersteller', 'Modultyp']]
    df_u = dark[SM_CURVE_U]
    df_i = dark[SM_CURVE_I]

    df_ds.columns = pd.MultiIndex.from_product([['STC'], df_ds.columns])
    df_m.columns = pd.MultiIndex.from_product([['Meta'], ['plant_name', 'string_name', 'in_serie', 'hersteller', 'modultyp']])
    df_u.columns = pd.MultiIndex.from_product([['U'], range(1, 251)])
    df_i.columns = pd.MultiIndex.from_product([['I'], range(1, 251)])

    df_m = df_ds.join(df_m)
    df_iv = df_u.join(df_i)

    return df_m.join(df_iv, how='right')