import pandas as pd
import pvserve
import numpy
import sys
from time import time
from tensorflow.keras import metrics
from tensorflow.keras.callbacks import TensorBoard
from tensorflow.keras.layers import Dense
from tensorflow.keras.models import Sequential
from tensorflow.keras.models import load_model
from sklearn.model_selection import train_test_split


data_file = "res/normalized_trainingsdata.csv"
data = pd.read_csv(data_file)
model_file_path = 'mlp.model'

def training_target_data(dataframe):
    training_columns = []
    target_columns = []
    for val in data.columns.values:
        if "dark" in val and "max" not in val:
            training_columns.append(val)
        elif "bright" in val and "max" not in val:
            target_columns.append(val)
        elif "temp" == val:
            training_columns.append(val)
        elif "E eff" == val:
            training_columns.append(val)
    return dataframe[training_columns], dataframe[target_columns]

def train(training_data, training_data_target, hidden, batch_size, epochs, file_path=model_file_path, layer_count=2, activation_f='sigmoid'):
    # Build model
    model = Sequential()
    # Add hidden layer to model and choose activation function for neurons
    model.add(Dense(hidden, activation=activation_f, input_dim=training_data.shape[1], kernel_initializer='normal'))
    for i in range(layer_count-1):
        model.add(Dense(hidden, activation=activation_f, input_dim=hidden, kernel_initializer='normal'))
    
    # Add output layer
    model.add(Dense(training_data_target.shape[1], kernel_initializer='normal'))
    # Choose optimizer and loss function
    model.compile(optimizer='adam', loss='mean_squared_error', metrics=[metrics.mse])
    # Add Tensorboard, view logs by cmd: tensorboard --logdir=logs/
    tensorboard = TensorBoard(log_dir="logs\{}".format(time()))
    # Training
    model.fit(training_data, training_data_target, batch_size=batch_size, epochs=epochs, callbacks=[tensorboard])
    # Save model
    model.save(file_path)
    return file_path

def predict(test_data, test_labels, lastModelFilePath=model_file_path):
    # Laden des Neuronalen Netzes
    model = load_model(lastModelFilePath)

    # Testen des Neuronalen Netzes
    error = model.evaluate(test_data, test_labels)
    predictions = model.predict(test_data)
    
    # Berechnen der Werte
    failures=[]
    for idx in range(0, len(predictions)):
        value = 100*(safe_div(predictions[idx].item(0), test_labels.values[idx].item(0))-1)
        failures.append(value)
    accuracy = 1 - error[0]
    mean_square_error = error[1]
    must_values = test_labels.values
    return accuracy, mean_square_error, predictions, must_values, failures

def safe_div(x, y):
    if y == 0:
        return 0
    return x / y

traine, test = train_test_split(data, test_size=0.4)

training_data, training_data_target = training_target_data(traine)
test_data, test_data_target = training_target_data(test)

dv = pvserve.data_visualisation.Visualisation()

dv.plot_graph(training_data_target.head(), "bright")
sys.exit()

print(" ")
null_columns=training_data.columns[training_data.isnull().any()]
print(training_data[null_columns].isnull().sum())
print(" ")
null_columns2=training_data_target.columns[training_data_target.isnull().any()]
print(training_data_target[null_columns2].isnull().sum())
zero_columns = training_data_target.columns[(training_data_target == 0).any()]
print(len(training_data_target[zero_columns]))

train(training_data, training_data_target, hidden=20, batch_size=4, epochs=50, file_path=model_file_path, layer_count=2, activation_f='relu')
accuracy, mean_square_error, predictions, must_values, failures = predict(pd.DataFrame(test_data), pd.DataFrame(test_data_target))

print("accuracy")
print(accuracy)
print("mean_square_error")
print(mean_square_error)
print("predictions")
print(predictions)
print("must_values")
print(must_values)
print("failures")
print(failures)