import pandas as pd
import numpy as np
from scipy import interpolate

def __calc_spline(row, drop_last=False):
    x = row.U.to_numpy().astype(float) 
    y = row.I.to_numpy().astype(float) 
    x = x[np.isfinite(y)]
    y = y[np.isfinite(y)]
    x, i = np.unique(x, return_index=True)
    y = y[i]
    
    if drop_last:
        x = x[:-1]
        y = y[:-1]

    f = interpolate.UnivariateSpline(x, y, s=0, k=1)
    x = np.linspace(0, x.max(), num=20)
    f = interpolate.UnivariateSpline(x, f(x), s=0, k=3)

    return f._eval_args

def __calc_dark_features(args):
    f = interpolate.UnivariateSpline._from_tck(args)
    x = np.linspace(0, 1, 200)
    y = f(x)
    
    # Leistung und Maximum ermitteln
    p = (y + 1) * x
    mpp_i = np.argmax(p)
    mpp_x = x[mpp_i]
    mpp_y = y[mpp_i]

    # Steigung M1 und M2 ermitteln
    m1_x = mpp_x - 0.15
    m1_m = 0

    m2_y = mpp_y - 0.15
    m2_m = 0

    if m1_x >= 0 and m1_x <= 1:
        m1_m = f.derivatives(m1_x)[1]

    if m2_y >= y[-1] and m2_y <= y[0]:
        x = interpolate.UnivariateSpline(x, y - m2_y, s=0).roots()[0]
        m2_m = f.derivatives(x)[1]

    return pd.Series({'Umpp':mpp_x, 'Impp':mpp_y, 'M1':m1_m, 'M2':m2_m})

def __interpolate_curve(args, points):
    f = interpolate.UnivariateSpline._from_tck(args)
    x = np.linspace(0, 1, points)
    return pd.Series(f(x))

def extract_spline(df, drop_last=False):
    return df.apply(__calc_spline, axis=1, args={drop_last: drop_last})

def extract_dark_features(df, spline=None, points=20):
    if spline is None:
        spline = extract_spline(df, drop_last=True)

    features = spline.apply(__calc_dark_features)
    features.columns = pd.MultiIndex.from_product([['Features'], features.columns])

    curves = spline.apply(__interpolate_curve, args={points: points}) + 1
    curves = curves.clip(-1, 1)
    curves.columns = pd.MultiIndex.from_product([['IV'], curves.columns])

    return df.join(features).join(curves)

def extract_bright_features(df, spline=None, points=20):
    if spline is None:
        spline = extract_spline(df)

    features = df.Char
    features.columns = pd.MultiIndex.from_product([['Features'], features.columns])

    curves = spline.apply(__interpolate_curve, args={points: points})
    curves = curves.clip(-1, 1)
    curves.columns = pd.MultiIndex.from_product([['IV'], curves.columns])

    result = df.join(features).join(curves)
    result = result[result.IV[19] < 0]

    return result