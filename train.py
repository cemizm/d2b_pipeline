import pvserve
import argparse
import logging, os

logging.disable(logging.WARNING)
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

print("--------------------- Parse Arguments ----------------------")
parser = argparse.ArgumentParser()
parser.add_argument("--experiment", "-e", required=True, type=int, help="set experiment to train")
args = parser.parse_args()

exp = args.experiment

print("Experiment:\t\t\t{}".format(exp))

param_layers = None
param_neurons = None
param_epochs = None
param_init = None

x_cols = None
y_cols = None
name = "E{}".format(exp)

if exp == 1:
    param_layers = [1]
    param_neurons = [0.3, 0.6, 0.9, 1.2]
    param_epochs = [20, 50, 100, 150, 200]
    param_init = [1, .6, 'tanh', 100, 'rmsprop', 0.001]

    x_cols = ['Env','Features_x']
    y_cols = ['Features_y']

elif exp == 2:
    param_layers = [1, 2]
    param_neurons = [0.3, 0.6, 0.9, 1.2]
    param_epochs = [100, 200, 500, 1000]
    param_init = [2, .6, 'tanh', 200, 'rmsprop', 0.001]

    x_cols = ['Env','IV_x']
    y_cols = ['Features_y']

elif exp == 3:
    param_layers = [1, 2]
    param_neurons = [0.9, 1.2, 1.5, 1.8]
    param_epochs = [200, 500, 1000, 1500, 2000]
    param_init = [2, .9, 'tanh', 1500, 'rmsprop', 0.001]

    x_cols = ['Env','IV_x']
    y_cols = ['IV_y']

if x_cols is None or y_cols is None:
    print("Invalid Experiment")
    exit()

print("------------------ Download from MLCycle -------------------")

client_ml = pvserve.mlcycle.Client()

test = client_ml.download_dataframe("dataset_test.csv", index_col=[0, 1, 2], header=[0, 1])
validate = client_ml.download_dataframe("dataset_validate.csv", index_col=[0, 1, 2], header=[0, 1])
train = client_ml.download_dataframe("dataset_train.csv", index_col=[0, 1, 2], header=[0, 1])

print("Dataset Test:\t\t\t{}".format(test.shape[0]))
print("Dataset Validate:\t\t{}".format(validate.shape[0]))
print("Dataset Train:\t\t\t{}".format(train.shape[0]))

print("-------------------------- Task ----------------------------")

print("Prepare Inputs...")
val_x = validate[x_cols]
val_y = validate[y_cols]

train_x = train[x_cols]
train_y = train[y_cols]

def train_model(layers, neurons, activation, epochs, optimizer, lr, verbose=0):
    model = pvserve.train.model_build(train_x.shape[1], 
                                      train_y.shape[1], 
                                      layers, 
                                      neurons, 
                                      lr=lr,
                                      activation=activation, 
                                      optimizer=optimizer)
    
    pvserve.train.model_fit(model, train_x, train_y, (val_x, val_y), epochs, 20, verbose=verbose)

    return model


def optimizer_train(layers, neurons, activation, epochs, optimizer, lr):
    model = train_model(layers, neurons, activation, epochs, optimizer, lr)

    return pvserve.train.model_evaluate(model, val_x, val_y, verbose=0)[0]

print("Prepare Hyperparameter...")
params = {
    'Interneschichten': param_layers,
    'Neuronenfaktor': param_neurons,
    'Aktivierungsfunktion': ['sigmoid', 'tanh'],
    'Trainingsepochen': param_epochs,
    'Optimierungsfunktion': ['adam', 'adagrad', 'rmsprop'],
    'Lernrate': [0.00001, 0.0001, 0.001, 0.01]
}

print("Start optimization...")
history = pvserve.train.optimize_run(params, param_init, optimizer_train)

print("Build final Model...")
model = train_model(*history.head(1).values[0][:-2], verbose=1)

print("--------------- Upload Optimization results ----------------")

client_ml.upload_model(model, 'Tensorflow Model E{}'.format(exp), 'model_e{}.h5'.format(exp))

client_ml.upload_dataframe(history, 'Optimization History E{}'.format(exp), 'opt_e{}.csv'.format(exp))
