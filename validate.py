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

client_ml = ml.Client()

model = client_ml.download_model("model.h5")

dataset = client_ml.download_dataframe("dataset.csv", low_memory=False)
ds_train, ds_test = pp.train_test_split(dataset, test_size=0.2)

result = pp.predict(model=model, 
                    dataset=ds_test,
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
                           ybinwidth=0.01)

client_ml.upload_plot(fig, "Test Error", "test.png")
exit()

result = result.sort_values(['rmse'])

fig = pp.plot_curves(curves=result.head(20),
                     index=INDEXES,
                     cols_source=COLS_IV_X,
                     cols_target=COLS_IV_Y,
                     cols_predict=COLS_IV_P)

client_ml.upload_plot(fig, "Top 20 Predictions", "top20_prediction.png")