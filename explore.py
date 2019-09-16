from pvserve import mlcycle as ml
from pvserve import smartmonitoring as sm
from pvserve import preprocessing as pp

COLS_U = ['Uoc', *sm.SM_CURVE_U]
COLS_I = ['Isc', *sm.SM_CURVE_I]

ISC_UOC_TOLERANCE = 1.1
FILTER_IRR = 600

print("------------------ Download from MLCycle -------------------")

client_ml = ml.Client()

meta = client_ml.download_dataframe("metadata.csv", index_col=[0, 1])
dark = client_ml.download_dataframe("raw_dark.csv", index_col=[0, 1])
bright = client_ml.download_dataframe("raw_bright.csv", index_col=[0, 1])

meta["Uoc_tol"] = meta.Uoc * ISC_UOC_TOLERANCE
meta["Isc_tol"] = meta.Isc * ISC_UOC_TOLERANCE

dark_meta = dark.join(meta, rsuffix="_meta")
bright_meta = bright.join(meta, rsuffix="_meta")

dark_meta = dark_meta.reset_index().set_index(['string_id', 'data_id'])
bright_meta = bright_meta.reset_index().set_index(['string_id', 'data_id'])

pp.standardize(dark_meta, COLS_U, COLS_I)
pp.standardize(bright_meta, COLS_U, COLS_I)

dark[[*COLS_U, *COLS_I]] = dark_meta[[*COLS_U, *COLS_I]]
bright[[*COLS_U, *COLS_I]] = bright_meta[[*COLS_U, *COLS_I]]

dark_count = len(dark.index)
bright_count = len(bright.index)

print("Bright IV-Curves:\t\t{}".format(bright_count))
print("Dark IV-Curves:\t\t\t{}".format(dark_count))

print("-------------------- Sanity Check Data ---------------------")

bright_summary = pp.check(bright_meta, FILTER_IRR)
dark_summary = pp.check(dark_meta, FILTER_IRR)

bright_grp = bright_summary.groupby(['plant_name', 'string_name']).sum().astype(int)
dark_grp = dark_summary.groupby(['plant_name', 'string_name']).sum().astype(int)

summary = dark_grp.join(bright_grp, lsuffix='_dark', rsuffix='_bright')

summary.insert(0, 'remaining', summary.remaining_dark * summary.remaining_bright)
summary.insert(0, 'total', summary.total_dark * summary.total_bright)

client_ml.upload_dataframe(summary, 'Error Summary', 'error_summary.csv')

drop_bright_len = len(bright_summary[bright_summary['remove']])
drop_dark_len = len(dark_summary[dark_summary['remove']])

print("Bright IV-Curve Errors:\t\t{}".format(drop_bright_len))
print("Dark IV-Curves Errors:\t\t{}".format(drop_dark_len))

print("-------------------- Upload Clean Data ---------------------")

bright = bright.drop(bright_summary[bright_summary['remove']].index)
dark = dark.drop(dark_summary[dark_summary['remove']].index)

print("Remaining bright IV-Curves:\t{}".format(bright.shape[0]))
print("Remaining dark IV-Curves:\t{}".format(dark.shape[0]))

client_ml.upload_dataframe(bright, 'Bright Curves Clean', 'clean_bright.csv')
client_ml.upload_dataframe(dark, 'Dark Curves Clean', 'clean_dark.csv')

