import pvserve

print("------------------ Download from MLCycle -------------------")

client_ml = pvserve.mlcycle.Client()

dark = client_ml.download_dataframe("clean_dark.csv", index_col=[0, 1], header=[0, 1])
bright = client_ml.download_dataframe("clean_bright.csv", index_col=[0, 1], header=[0, 1])

dark_count = len(dark.index)
bright_count = len(bright.index)

print("Bright IV-Curves:\t\t{}".format(bright_count))
print("Dark IV-Curves:\t\t\t{}".format(dark_count))

print("-------------------------- Task ----------------------------")

print("Extract Features...")
dark = pvserve.preprocessing.extract_dark_features(dark)
bright = pvserve.preprocessing.extract_bright_features(bright)

print("Combine IV-Curves...")
dataset = pvserve.preprocessing.dataset_combine(dark, bright)

print("Split Dataset...")
train, validate, test = pvserve.preprocessing.dataset_split(dataset)

print("--------------------- Upload Dataset ----------------------")

print("Dataset Test:\t\t\t{}".format(test.shape[0]))
print("Dataset Validate:\t\t{}".format(validate.shape[0]))
print("Dataset Train:\t\t\t{}".format(train.shape[0]))

client_ml.upload_dataframe(test, 'Dataset Test', 'dataset_test.csv')
client_ml.upload_dataframe(validate, 'Dataset Validate', 'dataset_validate.csv')
client_ml.upload_dataframe(train, 'Dataset Train', 'dataset_train.csv')