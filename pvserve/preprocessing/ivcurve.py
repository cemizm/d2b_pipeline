import pandas as pd
import numpy as np

def check(df):
    err = df.Uoc_meta.isnull() 
    err = err | df.Isc_meta.isnull()
    err = err | (df.Uoc > df.Uoc_tol) 
    err = err | (df.Isc > df.Isc_tol)
    err = err | (df.Uoc < 0)
    err = err | (df.Isc < 0)

    return err

def group_by_string(df, rows, cols):
    grp = df[rows][cols]
    grp = grp.reset_index().drop(columns='data_id')
    grp = grp.drop_duplicates().reset_index(drop=True)

    return grp

def standardize(df, cols_u, cols_i):
    df[cols_u] = df[cols_u].divide(df["Anzahl Module in Serie"], axis="index")
    df[cols_i] = df[cols_i].divide(df["Anzahl Module parallel"], axis="index")

def filter(df, irradiance):

    filter = df['E eff'] <= irradiance

    return filter

def filter_typ(df):
    return df.Kennlinientyp == "bright"

def normalize(df, cols_u, cols_i):
    df[cols_u] = df[cols_u].divide(df.Uoc_tol, axis="index")
    df[cols_i] = df[cols_i].divide(df.Isc_tol, axis="index")

def empty_iv(size, column=0, min=0, max=1):
    div = max / size

    value = np.full(size + 1, np.nan)
    index = np.arange(min, max + div, div)

    return pd.DataFrame({column: value}, index=index)

def interpolate(x, y, size):
    
    iv = pd.DataFrame({0: y}, index=x)
    iv = iv.dropna(how='all')
    
    empty = empty_iv(size)

    iv = empty.combine_first(iv).sort_index()

    iv = iv.loc[~iv.index.duplicated(keep='first')]

    iv = iv.interpolate(method = 'slinear')
    iv = iv.interpolate(method = 'spline', order=5, fill_value="extrapolate")

    return iv
