import pvserve

import pandas as pd
import os

TP_B = pvserve.smartmonitoring.SM_TYPE_BRIGHT
TP_D = pvserve.smartmonitoring.SM_TYPE_DARK
TP_PLANT = pvserve.smartmonitoring.SM_TYPE_PLANT
TP_STRING = pvserve.smartmonitoring.SM_TYPE_STRING
TP_MODUL = pvserve.smartmonitoring.SM_TYPE_MODUL

client_sm = pvserve.smartmonitoring.Client()
client_ml = pvserve.mlcycle.Client()
client_mdb = pvserve.moduldb.Client()

print()
print("---------------- Loading Observed Objects ------------------")

oo = client_sm.get_objects()

metadata = None
curves = {}

oo_data = oo[ (oo.type == TP_B) | (oo.type == TP_D) ]

print("Observed Objects:\t\t{}".format(len(oo.index)))
print("IV Curve Objects:\t\t{}".format(len(oo_data.index)))

print("------------------- Loading IV-Curves ----------------------")

for index, row in oo_data.iterrows():
    
    df = client_sm.get_data(index)
    if df is None:
        continue

    df.rename(columns={"id": "data_id"}, inplace=True)

    df.insert(0, "string_id", row.parent)
    df.set_index(["string_id", "data_id"], inplace=True)

    if row.type not in curves:
        curves[row.type] = df
    else:
        curves[row.type] = curves[row.type].append(df)

dark = curves[TP_D]
bright = curves[TP_B]

dark_count = len(dark.index)
bright_count = len(bright.index)

print("Bright IV-Curves:\t\t{}".format(bright_count))
print("Dark IV-Curves:\t\t\t{}".format(dark_count))

print("-------------------- Loading Metadata ----------------------")

metadata = client_sm.get_meta_dataframe_workaround()

plants = oo[oo.type == TP_PLANT][['name']]
strings = oo[(oo.type == TP_STRING) | (oo.type == TP_MODUL)][['name', 'parent']]
strings = strings.reset_index().set_index(['parent'])
header = strings.join(plants, lsuffix="_string", rsuffix="_plant")

header = header.reset_index()
header = header.rename(columns = { "index": "plant_id", 
                                   "id": "string_id", 
                                   "name_string": "string_name", 
                                   "name_plant": "plant_name"
                                })
header = header.set_index(["string_id"])

meta = header.join(metadata)

mdb = None
for elem in meta.Modultyp.unique():
    if elem is None:
        continue
    data = client_mdb.get_modul_data(elem)
    data = pd.DataFrame(data)
    if mdb is None:
        mdb = data
    else:
        mdb = mdb.append(data)

mdb = mdb.reset_index(drop = True)
mdb = mdb.set_index('Modultyp')
mdb = mdb.drop(columns=['Modulhersteller'])

meta = meta.join(mdb, on="Modultyp")

plants_count = len(plants.index)
string_count = len(strings.index)

print("Total Plants:\t\t\t{}".format(plants_count))
print("Total Strings:\t\t\t{}".format(string_count))

print("-------------------- Consolidate Data ----------------------")

bright = pvserve.ingestion.consolidate_bright(bright, meta)
dark = pvserve.ingestion.consolidate_dark(dark, meta)

print("-------------------- Upload to MLCycle ---------------------")

client_ml.add_metrics({
    'Plants': plants_count,
    'Strings': string_count,
    'Bright IV-Curves': bright_count,
    'Dark IV-Curves': dark_count
})

client_ml.upload_dataframe(dark, 'Dark IV-Curves (raw)', 'raw_dark.csv')
client_ml.upload_dataframe(bright, 'Bright IV-Curves (raw)', 'raw_bright.csv')
