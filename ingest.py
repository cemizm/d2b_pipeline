from pvserve import smartmonitoring as sm
from pvserve import mlcycle as ml
from pvserve import moduldb as mdb

import pandas as pd
import os

client_sm = sm.Client()
client_ml = ml.Client()
client_mdb = mdb.Client()

print()
print("---------------- Loading Observed Objects ------------------")

oo = client_sm.get_objects()

metadata = None
curves = {}

oo_data = oo[ (oo.type == sm.SM_TYPE_BRIGHT) | 
              (oo.type == sm.SM_TYPE_DARK) ]

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

dark = curves[sm.SM_TYPE_DARK]
bright = curves[sm.SM_TYPE_BRIGHT]

dark[sm.SM_CURVE_I] = dark[sm.SM_CURVE_I].multiply(-1, axis="index")

dark['Uoc'] = dark[sm.SM_CURVE_U].max(axis=1)
dark['Isc'] = dark[sm.SM_CURVE_I].max(axis=1)

dark_count = len(dark.index)
bright_count = len(bright.index)

print("Bright IV-Curves:\t\t{}".format(bright_count))
print("Dark IV-Curves:\t\t\t{}".format(dark_count))

print("-------------------- Loading Metadata ----------------------")

metadata = client_sm.get_meta_dataframe_workaround()

plants = oo[oo.type == sm.SM_TYPE_PLANT][['name']]
strings = oo[(oo.type == sm.SM_TYPE_STRING) | (oo.type == sm.SM_TYPE_MODUL)][['name', 'parent']]
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

print("-------------------- Upload to MLCycle ---------------------")

client_ml.add_metrics({
    'Plants': plants_count,
    'Strings': string_count,
    'Bright IV-Curves': bright_count,
    'Dark IV-Curves': dark_count
})

client_ml.upload_dataframe(meta, 'Metadata', 'raw_metadata.csv', 2)
client_ml.upload_dataframe(dark, 'Dark IV-Curves (raw)', 'raw_dark.csv', 2)
client_ml.upload_dataframe(bright, 'Bright IV-Curves (raw)', 'raw_bright.csv', 2)
