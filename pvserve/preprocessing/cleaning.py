import pandas as pd
import numpy as np

from .shared import *

def check_basic_bright(df, uoc_tol=1.2, isc_tol=1.2):
    result = pd.DataFrame(index=df.index)

    tol = get_stc_tol(df, uoc_tol, isc_tol)
    tol.Uoc = tol.Uoc * df.Meta.in_serie

    result['missing_meta']  = df.STC.Uoc.isnull() | df.STC.Isc.isnull()
    result['Uoc_gt_stc']   = df.Char.Uoc > tol.Uoc
    result['Isc_gt_stc']   = df.Char.Isc > tol.Isc
    result['Uoc_lt_zero']   = df.Char.Uoc < 0
    result['Isc_lt_zero']   = df.Char.Isc < 0

    return result

def check_basic_dark(df, uoc_tol=1.2, isc_tol=1.2):
    result = pd.DataFrame(index=df.index)

    tol = get_stc_tol(df, uoc_tol, isc_tol)
    tol.Uoc = tol.Uoc * df.Meta.in_serie

    result['missing_meta']  = df.STC.Uoc.isnull() | df.STC.Isc.isnull()
    result['Uoc_gt_stc']   = df.U.max(axis=1) > tol.Uoc
    result['Isc_gt_stc']   = df.I.min(axis=1) > tol.Isc
    result['Uoc_lt_zero']   = df.U.max(axis=1) < 0
    result['Isc_lt_zero']   = df.I.min(axis=1) > 0

    return result

def check_regression(df, uoc_tol=1.2, isc_tol=1.2, reg_tol=0.1):
    result = pd.DataFrame(index=df.index)

    tol = get_stc_tol(df, uoc_tol, isc_tol)

    norm = (df.Char.Isc / tol.Isc)

    err_tol = norm.max() * reg_tol 
    reg = np.polyfit(df.Env.Irr, norm, 1)
    err = reg[0] * df.Env.Irr + reg[1]

    result['Isc_to_high'] = norm > (err + err_tol)

    return result

def check_fillfactor(df, ff_tol=0.95):
    result = pd.DataFrame(index=df.index)

    result['fault'] = False
    grp = df.groupby(['string_id'])
    for _, items in grp:
        ff = (items.Char.Impp * items.Char.Umpp) / (items.Char.Isc * items.Char.Uoc)
        stats = ff[ff < 1].describe()
        result.loc[items.index, 'fault'] = (ff < stats['50%'] * ff_tol) | (ff > 0.9)
    
    return result

def check_slope(df, threshold=0.002):
    result = pd.DataFrame(index=df.index)

    lim = pd.DataFrame(index=df.index)

    tmp = df.U[df.U > 0]
    lim['u1'] = tmp.min(axis=1)
    lim['u1col'] = tmp.idxmin(axis=1)

    tmp = tmp.subtract(lim.u1, axis=0)
    tmp = tmp[tmp > 0]
    lim['u2'] = tmp.min(axis=1) + lim.u1
    lim['u2col'] = tmp.idxmin(axis=1)

    lim['i1'] = df.I.lookup(lim.u1col.index, lim.u1col.values)
    lim['i2'] = df.I.lookup(lim.u2col.index, lim.u2col.values)
    lim['steigung'] = (-lim.i2 - -lim.i1) / (lim.u2 - lim.u1)

    result['low_info'] = lim.steigung > threshold

    return result

def check_dark(df):
    basic = check_basic_dark(df)
    slope = check_slope(df)

    result = basic.join(slope)

    result['remove'] = result.any(axis=1)

    return result

def check_bright(df):
    basic = check_basic_bright(df)
    reg = check_regression(df)
    ff = check_fillfactor(df)
    
    result = basic.join(reg).join(ff)

    result['remove'] = result.any(axis=1)

    return result

def clean_dark(df):
    filter_dark = check_dark(df)
    df.drop(filter_dark[filter_dark.remove].index, inplace=True)

def clean_bright(df):
    filter_bright = check_bright(df)
    df.drop(filter_bright[filter_bright.remove].index, inplace=True)