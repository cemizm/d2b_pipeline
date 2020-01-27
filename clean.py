import pvserve

print("------------------ Download from MLCycle -------------------")

client_ml = pvserve.mlcycle.Client()

dark = client_ml.download_dataframe("raw_dark.csv", index_col=[0, 1], header=[0, 1])
bright = client_ml.download_dataframe("raw_bright.csv", index_col=[0, 1], header=[0, 1])

dark_count = len(dark.index)
bright_count = len(bright.index)

print("Bright IV-Curves:\t\t{}".format(bright_count))
print("Dark IV-Curves:\t\t\t{}".format(dark_count))

print("-------------------------- Task ----------------------------")

print("Filter Errors...")
pvserve.preprocessing.clean_dark(dark)
pvserve.preprocessing.clean_bright(bright)

print("Normalize Values...")
pvserve.preprocessing.transform_dark(dark)
pvserve.preprocessing.transform_bright(bright)

print("-------------------- Upload Clean Data ---------------------")

print("Remaining bright IV-Curves:\t{}".format(bright.shape[0]))
print("Remaining dark IV-Curves:\t{}".format(dark.shape[0]))

client_ml.upload_dataframe(bright, 'Bright Curves Clean', 'clean_bright.csv')
client_ml.upload_dataframe(dark, 'Dark Curves Clean', 'clean_dark.csv')