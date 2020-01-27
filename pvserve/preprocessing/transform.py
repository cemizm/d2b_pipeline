import pandas as pd
import numpy as np

from .shared import *

def standardize(df):
    df.U = df.U.divide(df.Meta.in_serie, axis="index")

def normalize_curve(df, uoc_tol=1.2, isc_tol=1.2):
    tol = get_stc_tol(df, uoc_tol, isc_tol)

    df.U = df.U.divide(tol.Uoc, axis="index")
    df.I = df.I.divide(tol.Isc, axis="index")

def normalize_char(df, uoc_tol=1.2, isc_tol=1.2):
    tol = get_stc_tol(df, uoc_tol, isc_tol)

    df.loc[:,('Char', 'Uoc')] = df.Char.Uoc / df.Meta.in_serie / tol.Uoc 
    df.loc[:,('Char', 'Isc')] = df.Char.Isc / tol.Isc
    df.loc[:,('Char', 'Umpp')] = df.Char.Umpp / df.Meta.in_serie / tol.Uoc
    df.loc[:,('Char', 'Impp')] = df.Char.Impp / tol.Isc

def normalize_env(df, temp=70, irr=1367):
    df.loc[:,('Env', 'Temp')] = df.Env.Temp / temp
    df.loc[:,('Env', 'Irr')] = df.Env.Irr / irr

def transform_dark(df, uoc_tol=1.2, isc_tol=1.2):
    standardize(df)
    normalize_curve(df, uoc_tol=uoc_tol, isc_tol=isc_tol)

def transform_bright(df, uoc_tol=1, isc_tol=1.2, temp=70, irr=1367):
    standardize(df)
    normalize_curve(df, uoc_tol=uoc_tol, isc_tol=isc_tol)
    normalize_char(df, uoc_tol=uoc_tol, isc_tol=isc_tol)
    normalize_env(df, temp=temp, irr=irr)

def dataset_combine(dark, bright):
    d1 = dark[['STC', 'Meta', 'Features', 'IV']].rename(columns={'Features': 'Features_x', 'IV': 'IV_x'})
    cols = d1.columns.values
    d1.columns = [col[0] + "_" + str(col[1]) for col in d1.columns]
    d1 = d1.reset_index()

    d2 = bright[['Env', 'Features', 'IV']].rename(columns={'Features': 'Features_y', 'IV': 'IV_y'})
    cols = np.concatenate((cols, d2.columns.values))
    d2.columns = [col[0] + "_" + str(col[1]) for col in d2.columns]
    d2 = d2.reset_index()

    d = pd.merge(d1, d2, on="string_id")
    d = d.set_index(['string_id', 'data_id_x', 'data_id_y'])
    d.columns = pd.MultiIndex.from_tuples(cols)

    return d

def dataset_split(df, test_size=0.25, val_size=0.2):
    test = df.sample(frac=test_size, random_state=130684)
    df = df.drop(test.index)
    
    validate = df.sample(frac=val_size, random_state=181186)
    df = df.drop(validate.index)

    return df, validate, test