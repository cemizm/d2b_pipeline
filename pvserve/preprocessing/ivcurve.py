import pandas as pd
import numpy as np

def check(df, irradiance):
    result = pd.DataFrame(df[['plant_name', 'string_name']])

    result['total'] = True
    result['remove'] = False
    result['remaining'] = True

    result['missing_meta']  = df.Uoc_meta.isnull() | df.Isc_meta.isnull()
    result['Uoc_gt_meta']   = df.Uoc > df.Uoc_tol
    result['Isc_gt_meta']   = df.Isc > df.Isc_tol
    result['Uoc_lt_zero']   = df.Uoc < 0
    result['Isc_lt_zero']   = df.Isc < 0

    if 'E eff' in df:
        result['low_irr'] = df['E eff'] < irradiance

    if 'Kennlinientyp' in df:
        result['is_bright'] = df['Kennlinientyp'] == 'bright'

    result['remove'] = result.iloc[:,5:].any(axis=1)
    result['remaining'] = ~result['remove']

    return result

def group_by_string(df, rows, cols):
    grp = df[rows][cols]
    grp = grp.reset_index().drop(columns='data_id')
    grp = grp.drop_duplicates().reset_index(drop=True)

    return grp

def standardize(df, cols_u, cols_i):
    df[cols_u] = df[cols_u].divide(df["Anzahl Module in Serie"], axis="index")
    df[cols_i] = df[cols_i].divide(df["Anzahl Module parallel"], axis="index")

def normalize(df, cols_u, cols_i):
    df[cols_u] = df[cols_u].divide(df.Uoc_tol, axis="index")
    df[cols_i] = df[cols_i].divide(df.Isc_tol, axis="index")

def normalize_bright(df, temp, irr):
    df['Temp'] = df['T mod'] / temp
    df['Irr'] = df['E eff'] / irr

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

def merge(dark, bright):
    dark = dark.reset_index().set_index("string_id")
    bright = bright.reset_index().set_index("string_id").drop(columns=['plant_id'])

    return pd.merge(dark, bright, on="string_id")

def summarize(dark, bright):
    dark = dark.groupby(['plant_name', 'string_name']).count()[['ts']]
    bright = bright.groupby(['plant_name', 'string_name']).count()[['ts']]

    dark.columns = ['dark']
    bright.columns = ['bright']

    total = dark.join(bright).fillna(0)
    total.bright = total.bright.astype(int)
    total['total'] = total.dark * total.bright

    return total
    



