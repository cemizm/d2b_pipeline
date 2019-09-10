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
    filter = df.Kennlinientyp == "bright"
    return filter

def normalize(df, cols_u, cols_i):
    df[cols_u] = df[cols_u].divide(df.Uoc_tol, axis="index")
    df[cols_i] = df[cols_i].divide(df.Isc_tol, axis="index")

def get_iv_cols(size=20, min=0, max=1):
    div = max / (size - 1)
    cols = ["IV" + str(i) for i in range(1, size + 1)]
    index = pd.Float64Index(np.arange(min, max + div, div))
    return index, cols

def interpolate(df, cols_u, cols_i, size=20, min=0, max=1):

    value = np.full(size, np.nan)
    index, cols = get_iv_cols(size)

    target = pd.DataFrame(columns=cols, index=df.index)

    for row_index, row in df.iterrows():
        x = row[cols_i].values
        y = row[cols_u].values
        iv = pd.DataFrame({0: x}, index=y).dropna(how="all")

        tmp = pd.DataFrame({0: value}, index=index)
        tmp = tmp.combine_first(iv).sort_index()

        tmp = tmp.loc[~tmp.index.duplicated(keep='first')]

        tmp = tmp.interpolate(method = 'slinear')
        tmp = tmp.interpolate(method = 'spline', order=5, fill_value="extrapolate")
        
        target.loc[row_index] = tmp.loc[index].T.values[0]
        
    return df.join(target)

def max_per_string(df, col):
    idx = df.groupby(['string_id'], sort=False)[col].transform(max) == df[col]
    return df[idx]

def plot(df, size, **kwargs):
    index, cols = get_iv_cols(size)

    df = df[cols].reset_index(drop=True).T
    df['index'] = index
    df = df.set_index(['index'])
    
    return df.plot(**kwargs)

    



