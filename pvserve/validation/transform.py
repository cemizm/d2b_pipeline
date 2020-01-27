import pandas as pd
import numpy as np
from scipy import interpolate

def __calc_spline(row):
    x = np.linspace(0, 1, len(row))
    y = row.to_numpy().astype(float) 
    f = interpolate.UnivariateSpline(x, y, s=0, k=3)

    return f._eval_args
    
def __interpolate_curve(args, x):
    f = interpolate.UnivariateSpline._from_tck(args)
    return pd.Series(f(x))

def __calc_mpp(args): 
    f = interpolate.UnivariateSpline._from_tck(args)

    x = np.linspace(0, 1, 200)
    y = f(x)

    p = y * x
    mpp_i = np.argmax(p)

    mpp_x = x[mpp_i]
    mpp_y = y[mpp_i]

    return pd.Series({'Umpp':mpp_x, 'Impp':mpp_y})

def extract_spline(df):
    return df.apply(__calc_spline, axis=1)
    
def extract_mpp(df, spline=None):
    if spline is None:
        spline = extract_spline(df)

    mpp = spline.apply(__calc_mpp)

    return mpp
    