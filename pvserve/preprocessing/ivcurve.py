import pandas as pd
import numpy as np

import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D


def check_bright(df, uoc_tol=1.2, isc_tol=1.2, threshold=0.95, reg_tol=0.1):
    result = pd.DataFrame(index=df.index)

    tol = pd.DataFrame(index=df.index)
    tol['Uoc'] = df['Uoc_meta'] * uoc_tol
    tol['Isc'] = df['Isc_meta'] * isc_tol

    # Basic checks
    result['missing_meta']  = df.Uoc_meta.isnull() | df.Isc_meta.isnull()
    result['Uoc_gt_meta']   = df.Uoc > tol.Uoc
    result['Isc_gt_meta']   = df.Isc > tol.Isc
    result['Uoc_lt_zero']   = df.Uoc < 0
    result['Isc_lt_zero']   = df.Isc < 0

    # FF based check
    result['fault'] = False
    grp = df.groupby(['string_id'])
    for _, items in grp:
        ff = (items.Ipmax * items.Upmax) / (items.Isc * items.Uoc)
        stats = ff[ff < 1].describe()
        result.loc[items.index, 'fault'] = (ff < stats['50%'] * threshold) | (ff > 0.9)
        #result.loc[items.index, 'fault'] = (stats['50%'] - (ff - stats['std'])) < 0

    # Regression based check
    err_tol = (df['Isc'] / tol.Isc).max() * reg_tol 
    reg = np.polyfit(df['E eff'], (df['Isc'] / tol.Isc), 1)
    err = reg[0] * df['E eff'] + reg[1]
    result['Isc_to_high'] = (df['Isc'] / tol.Isc) > (err + err_tol)

    return result

def check_dark(df, cols_u, threshold=0.03):
    result = pd.DataFrame(index=df.index)

    cols = df[cols_u]

    result['missing_meta']  = df.Uoc_meta.isnull() | df.Isc_meta.isnull()
    result['Uoc_lt_zero']   = df.Uoc < 0
    result['Isc_lt_zero']   = df.Isc < 0

    lim = pd.DataFrame(index=df.index)

    tmp = cols[cols > 0]
    lim['u1'] = tmp.min(axis=1)
    lim['u1col'] = tmp.idxmin(axis=1).str.replace('U', 'I')

    tmp = tmp.subtract(lim.u1, axis=0)
    tmp = tmp[tmp > 0]
    lim['u2'] = tmp.min(axis=1) + lim.u1
    lim['u2col'] = tmp.idxmin(axis=1).str.replace('U', 'I')

    lim['i1'] = df.lookup(lim.u1col.index, lim.u1col.values)
    lim['i2'] = df.lookup(lim.u2col.index, lim.u2col.values)
    lim['steigung'] = (lim.i2 - lim.i1) / (lim.u2 - lim.u1)

    result['low_info'] = lim.steigung > threshold

    return result

def balanceData(df, col='E eff'):
    result = pd.DataFrame(index=df.index)

    value_range = df[col].max() - df[col].min()
    value_count = df[col].count()
    count_per_item = value_count / value_range

    value_median = df[col].median()
    target_range = value_median / count_per_item

    lower_area = df[df[col] < value_median]

    target_frac = target_range / lower_area[col].count() 
    lower_area = lower_area.sample(frac = 1 - target_frac)

    result['balance'] = df.index.isin(lower_area.index)

    return result

def getErrorSummary(df):
    result = pd.DataFrame(index=df.index)

    result['total'] = True
    result['remove'] = df.any(axis=1)
    result['remaining'] = ~result['remove']

    return result

def summarize(bright, dark, meta):
    m = meta.reset_index(level=1)
    m['Modultyp'] = m['Modulhersteller'] + " " + m['Modultyp']
    d = dark.reset_index(level=1)
    d = d[['data_id']].join(m[['plant_name', 'string_name']]).reset_index()

    b = bright.reset_index(level=1)
    b = b[['data_id']].join(m[['plant_name', 'string_name']]).reset_index()

    dgp = d.groupby(['plant_name'])
    bgp = b.groupby(['plant_name'])
    mgp = m.groupby(['plant_name'])

    dgs = d.groupby(['plant_name', 'string_name'])
    bgs = b.groupby(['plant_name', 'string_name'])

    count_string = bgs.first().groupby(['plant_name']).count()['string_id']
    count_bright = bgp.count()['string_id']
    count_dark = dgp.count()['string_id']
    avg_serie = mgp.mean()['Anzahl Module in Serie'].round(0).astype("Int32")

    target = mgp.first()[['Modultyp', 'Zelltyp', 'Baujahr']]

    target['Modultyp'] = target['Modultyp'].str.replace('LG Electronics USA LG', 'LG USA')

    target['Zelltyp'] = target['Zelltyp'].str.replace('Dünschicht', 'thin')
    target['Zelltyp'] = target['Zelltyp'].str.replace('monokristallin n-type \nrückseitenkontaktiert', 'mono-n')
    target['Zelltyp'] = target['Zelltyp'].str.replace('monokristallin n-type', 'mono-n')
    target['Zelltyp'] = target['Zelltyp'].str.replace('monokristallin p-type', 'mono-p')
    target['Zelltyp'] = target['Zelltyp'].str.replace('polykristallin', 'poly')

    target['Baujahr'] = target['Baujahr'].str.replace('\?\?', 'NaN')
    target['Baujahr'] = target['Baujahr'].str.replace('\?', 'NaN')

    target.insert(0, "Dunkel", count_dark.astype("Int32"))
    target.insert(0, "Hell", count_bright.astype("Int32"))
    target.insert(0, "Serie", avg_serie.astype("Int32"))
    target.insert(0, "Strings", count_string.astype("Int32"))

    target = target.dropna(how='all')

    return target

def group_by_string(df, rows, cols):
    grp = df[rows][cols]
    grp = grp.reset_index().drop(columns='data_id')
    grp = grp.drop_duplicates().reset_index(drop=True)

    return grp

def standardize(df, cols_u, cols_i):
    df[cols_u] = df[cols_u].divide(df["Anzahl Module in Serie"], axis="index")
    df[cols_i] = df[cols_i].divide(df["Anzahl Module parallel"], axis="index")

def normalize_dark(df, cols_u, cols_i, uoc_tol=1.2, isc_tol=1.2):
    tol = pd.DataFrame(index=df.index)
    tol['Uoc'] = df['Uoc_meta'] * uoc_tol
    tol['Isc'] = df['Isc_meta'] * isc_tol

    df[cols_u] = df[cols_u].divide(tol.Uoc, axis="index")
    df[cols_i] = df[cols_i].divide(tol.Isc, axis="index")

def normalize_bright(df, cols_u, cols_i, uoc_tol=1.2, isc_tol=1.2, temp=70, irr=1367):

    normalize_dark(df, cols_u, cols_i, uoc_tol, isc_tol)

    df['Temp'] = df['T mod'] / temp
    df['Irr'] = df['E eff'] / irr

def get_iv_cols(size=20, min=0, max=1):
    div = max / (size - 1)
    cols = ["IV" + str(i) for i in range(1, size + 1)]
    index = pd.Float64Index(np.arange(min, max + div, div))
    return index, cols

def interpolate_bright(df, cols_u, cols_i, size=20, min=0, max=1):

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

def interpolate_dark(df, cols_u, cols_i, size=20, min=0, max=1):
    all = [*cols_u, *cols_i]

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
        tmp.loc[:tmp.first_valid_index()] = 0

        tmp = tmp.interpolate(method = 'slinear', fill_value='extrapolate')
        
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

def plot_distribution(df, width=8, height=1.5):
    plot_cols = ['E eff', 'T mod', 'Isc', 'Uoc']
    col_names = ['Einstrahlung', 'Temperatur', 'Kurzschlusstrom', 'Leerlaufspannung']

    cols = len(plot_cols)

    fig, axis = plt.subplots(cols, 1, figsize=(width, cols * height))

    plot_data = df[plot_cols]

    for i in range(0, cols):
        hue = None
        box = None
        if 'remove' in df:
            hue = df['remove']
            box = df[df['remove']==False][plot_cols[i]]

        plot_feature_distribution(plot_data[plot_cols[i]], col_names[i], axis[i], hue, box)

    fig.tight_layout()

    lines = [Line2D([0], [0], color='red', ls='-', lw=3),
            Line2D([0], [0], color='green', ls='--', lw=3),
            Line2D([0], [0], color='w', markerfacecolor='limegreen', marker='o', markersize=10)]

    titles = ['Median', 'Durchschnitt', 'Datensatz']

    if 'remove' in df:
        lines.append(Line2D([0], [0], color='w', markerfacecolor='lightcoral', marker='o', markersize=10))
        titles.append('Entfernt')


    fig.legend(lines, titles)

    return fig

def plot_feature_distribution(data, name, ax, data_hue=None, data_box=None):
    if data_box is None:
        data_box = data
        
    boxprops = dict(linestyle='-', linewidth=2, edgecolor='midnightblue')
    lineprops = dict(linestyle='-', linewidth=2, color='midnightblue')
    medianprops = dict(linestyle='-', linewidth=3, color='red')
    meanprops = dict(linestyle='--', linewidth=3, color='green')
    
    colors = ['limegreen', 'lightcoral']
    
    sns.swarmplot(x=data, y=[""]*len(data), 
                  hue=data_hue, ax=ax,
                  palette=colors, size=2)
    
    sns.boxplot(x=data_box, ax=ax, color='lightblue',
                width=0.7,
                meanline=True,
                showmeans=True, 
                showfliers=False,
                boxprops=boxprops,
                medianprops=medianprops,
                meanprops=meanprops,
                capprops=lineprops,
                whiskerprops=lineprops)
    
    ax.set_xlabel(None)
    ax.title.set_text(name)
    legend = ax.get_legend()
    if legend is not None:
        legend.remove()