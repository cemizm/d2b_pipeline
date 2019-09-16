import matplotlib.pyplot as plt

from pvserve import mlcycle as ml
from pvserve import smartmonitoring as sm
from pvserve import preprocessing as pp

COLS_U = ['Uoc', *sm.SM_CURVE_U]
COLS_I = ['Isc', *sm.SM_CURVE_I]

ISC_UOC_TOLERANCE = 1.1

INTERPOLATE_X = 20
INTERPOLATE_ERROR_BRIGHT = 0.4

NORMALIZE_TEMP = 70
NORMALIZE_IRR = 1367

INDEXES, COLS = pp.get_iv_cols(INTERPOLATE_X)

print("------------------ Download from MLCycle -------------------")

client_ml = ml.Client()

meta = client_ml.download_dataframe("metadata.csv", index_col=[0, 1])
dark = client_ml.download_dataframe("clean_dark.csv", index_col=[0, 1])
bright = client_ml.download_dataframe("clean_bright.csv", index_col=[0, 1])

### Prepare data

meta["Uoc_tol"] = meta.Uoc * ISC_UOC_TOLERANCE
meta["Isc_tol"] = meta.Isc * ISC_UOC_TOLERANCE

dark_meta = dark.join(meta, rsuffix="_meta")
bright_meta = bright.join(meta, rsuffix="_meta")

dark_count = len(dark.index)
bright_count = len(bright.index)

print("Bright IV-Curves:\t\t{}".format(bright_count))
print("Dark IV-Curves:\t\t\t{}".format(dark_count))

print("--------------------- Normalize Data -----------------------")

pp.normalize(dark_meta, COLS_U, COLS_I)
pp.normalize(bright_meta, COLS_U, COLS_I)

pp.normalize_bright(bright_meta, NORMALIZE_TEMP, NORMALIZE_IRR)

fig, ax = plt.subplots(figsize=(18, 10))

ax.scatter(bright_meta['E eff'], 
           (bright_meta['Uoc'] * bright_meta['Isc']))

ax.set_xlabel('Irradiance')
ax.set_ylabel('Watt @ Ideal (normalized)')

client_ml.upload_plot(fig, "Data Distribution (Bright)", "dd_bright.png")

fig, ax = plt.subplots(figsize=(18, 10))

ax.scatter(dark_meta['Uoc'], dark_meta['Isc'])

ax.set_xlabel('Uoc (normalized)')
ax.set_ylabel('Isc (normalized)')

client_ml.upload_plot(fig, "Data Distribution (Dark)", "dd_dark.png")

print("---------------------- Interpolation -----------------------")

print("Interpolation Points:\t\t{}".format(INTERPOLATE_X))

dark_meta = pp.interpolate(dark_meta, sm.SM_CURVE_U, sm.SM_CURVE_I, size=INTERPOLATE_X)
bright_meta = pp.interpolate(bright_meta, sm.SM_CURVE_U, sm.SM_CURVE_I, size=INTERPOLATE_X)

# Drop interpolation errors
bright_meta = bright_meta.drop(bright_meta[bright_meta['IV' + str(INTERPOLATE_X)] > INTERPOLATE_ERROR_BRIGHT].index)

# Clip to -1 - 1
dark_meta[COLS] = dark_meta[COLS].clip(-1, 1)
bright_meta[COLS] = bright_meta[COLS].clip(-1, 1)

#plot interpolated curves
fig, ax = plt.subplots(figsize=(18, 10))

max_isc = pp.max_per_string(dark_meta, 'Isc')
pp.plot(max_isc, INTERPOLATE_X, ax=ax, legend=False, ylim=(0,1))

ax.set_xlabel('U (normalized)')
ax.set_ylabel('I (normalized)')

client_ml.upload_plot(fig, "Dark IV-Curves", "dark_visual.png")


fig, ax = plt.subplots(figsize=(18, 10))

max_isc = pp.max_per_string(bright_meta, 'Isc')
pp.plot(max_isc, INTERPOLATE_X, ax=ax, legend=False, ylim=(0,1))

ax.set_xlabel('U (normalized)')
ax.set_ylabel('I (normalized)')

client_ml.upload_plot(fig, "Bright IV-Curves", "bright_visual.png")

print("-------------------- Merge training set --------------------")

#remove overlapping meta columns
sbright = bright_meta.drop(columns=['Isc_meta', 'Uoc_meta', *meta.columns.drop(['Isc', 'Uoc'])])

combined = pp.merge(dark_meta, sbright)

summary = pp.summarize(dark_meta, bright_meta)

print("Dataset size:\t\t\t{}".format(combined.shape[0]))

client_ml.upload_dataframe(summary, 'Dataset Summary', 'dataset_summary.csv')
client_ml.upload_dataframe(combined, 'Dataset', 'dataset.csv')

client_ml.add_metrics({
    'Dataset': combined.shape[0]
})