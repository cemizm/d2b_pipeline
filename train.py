import logging, os

from pvserve import mlcycle as ml
from pvserve import preprocessing as pp

logging.disable(logging.WARNING)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

IV_COLS = 20

INDEXES, COLS = pp.get_iv_cols(IV_COLS)

COLS_IV_X = [c + '_x' for c in COLS] # Dark Curve Labels
COLS_IV_Y = [c + '_y' for c in COLS] # Bright Curve Labels
COLS_IV_P = [c + '_p' for c in COLS] # Predict Curve Labels
COLS_IV_T = [*COLS_IV_X, *COLS_IV_Y] # Ground Truth Curve Labels

COLS_X = ["Temp", "Irr", *COLS_IV_X]
COLS_Y = [*COLS_IV_Y, 'Uoc_y']
COLS_P = [*COLS_IV_P, 'Uoc_p']

PARAM_HIDDEN_LAYERS = 2
PARAM_PER_LAYER_FACTOR = 2
PARAM_EPOCHS = 10
PARAM_BATCH_SIZE = 10

PARAM_OPTIMIZER = 'rmsprop'

print("------------------ Download from MLCycle -------------------")

client_ml = ml.Client()

dataset = client_ml.download_dataframe("dataset.csv", low_memory=False)

dataset[COLS_IV_T] = dataset[COLS_IV_T].clip(-1, 1)

ds_train, ds_test = pp.train_test_split(dataset, test_size=0.2)

print("Train Dataset:\t\t\t{}".format(ds_train.shape[0]))
print("Test Dataset:\t\t\t{}".format(ds_test.shape[0]))

print("----------------------- Build model ------------------------")

model = pp.build_model(input_size=len(COLS_X), 
                       output_size=len(COLS_Y),
                       hidden_layer=PARAM_HIDDEN_LAYERS,
                       neurons_per_layer=(len(COLS_X) * PARAM_PER_LAYER_FACTOR),
                       optimizer=PARAM_OPTIMIZER,
                       activation='tanh')

model.summary()
print()

print("Batch Size:\t\t\t{}".format(PARAM_BATCH_SIZE))
print("Training Epochs:\t\t{}".format(PARAM_EPOCHS))

history = model.fit(ds_train[COLS_X], 
                    ds_train[COLS_Y], 
                    epochs=PARAM_EPOCHS, 
                    batch_size=PARAM_BATCH_SIZE, 
                    shuffle=True, 
                    validation_split=0.25, 
                    verbose=0)

client_ml.upload_model(model, "Tensorflow Model", "model.h5")

fig = pp.plot_history(history)
client_ml.upload_plot(fig, "Model loss", "model_loss.png")

print()
print("------------------------ Error Plot ------------------------")

result = pp.predict(model=model, 
                    dataset=dataset,
                    cols_x=COLS_X,
                    cols_predict=COLS_P)

result = pp.calculate_rmse(dataset=result, 
                           cols_predict=COLS_IV_P,
                           cols_y=COLS_IV_Y)

fig = pp.plot_scatter_bins(x=result['E eff'].values, 
                           y=result['rmse'].values, 
                           xlabel='Einstrahlung',
                           ylabel='RMSE',
                           xbinwidth=50,
                           ybinwidth=0.001)

client_ml.upload_plot(fig, "RMSE", "model_rmse.png")

print("----------------------- Predictions ------------------------")
result = pp.predict(model=model, 
                    dataset=ds_test,
                    cols_x=COLS_X,
                    cols_predict=COLS_P)

samples = result.sample(50)

fig = pp.plot_curves(curves=samples,
                     index=INDEXES,
                     cols_source=COLS_IV_X,
                     cols_target=COLS_IV_Y,
                     cols_predict=COLS_IV_P)

client_ml.upload_plot(fig, "Prediction Examples", "model_prediction.png")