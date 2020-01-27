import pandas as pd

def get_stc_tol(df, uoc_tol=1.2, isc_tol=1.2):
    tol = pd.DataFrame(index=df.index)

    tol['Uoc'] = df.STC.Uoc * uoc_tol
    tol['Isc'] = df.STC.Isc * isc_tol

    return tol