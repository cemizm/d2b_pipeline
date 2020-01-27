import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense

def train_test_split(dataset, test_size=0.2):
    weights = pd.DataFrame(index = dataset.string_id.unique()).sort_index()

    weights['weights'] = dataset.groupby(['string_id']).count()['data_id_x'].sort_index()
    weights.weights = 1 - (weights.weights / weights.weights.sum())
    weights.weights = weights.weights / weights.weights.sum()

    weights = dataset[['string_id']].join(weights.weights, on="string_id").weights

    test = dataset.sample(frac=test_size, random_state=130684)#, weights=weights)
    train = dataset.drop(test.index).reset_index()
    
    test = test.reset_index()

    return train, test

def build_model(input_size, 
                output_size, 
                hidden_layer, 
                neurons_per_layer, 
                optimizer='rmsprop', 
                activation='tanh', 
                loss='mse', 
                metrics=['accuracy']):
    model = Sequential()

    model.add(Dense(neurons_per_layer, activation=activation, input_shape=(input_size,)))

    for i in range(0, hidden_layer):
        model.add(Dense(neurons_per_layer, activation=activation))

    model.add(Dense(output_size, activation=activation))

    model.compile(loss=loss,
                  optimizer=optimizer, 
                  metrics=metrics)

    return model

def predict(model, dataset, cols_x, cols_predict):
    pred_y = model.predict(dataset[cols_x])
    pred_y = pd.DataFrame(pred_y, columns=cols_predict)

    return dataset.join(pred_y)


def calculate_rmse(dataset, cols_predict, cols_y, col_rmse='rmse'):
    result = pd.DataFrame(index=dataset.index)
    result[col_rmse] = 0

    cols = len(cols_predict)
    for i in range(0, cols):
        error = dataset[cols_y[i]] - dataset[cols_predict[i]]
        result[col_rmse] += error ** 2

    result[col_rmse] = (result[col_rmse] / cols) **.5

    return dataset.join(result)

def plot_history(history):
    fig, ax = plt.subplots(figsize=(18, 10))
    ax.plot(history.history['loss'])
    ax.plot(history.history['val_loss'])
    ax.set_title('Model loss')
    ax.set_xlabel('Epoch')
    ax.set_ylabel('Loss')
    ax.legend(['Loss Train', 'Loss Validation'], loc='upper right')

    return fig

def plot_scatter_bins(x, y, xlabel, ylabel, xbinwidth = 50, ybinwidth = 0.001):
    fig, ax = plt.subplots(figsize=(18, 15))

    ax.scatter(x, y)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

    ymin = int(np.min(y)/ybinwidth) * ybinwidth
    xmin = int(np.min(x)/xbinwidth) * xbinwidth

    ymax = int(np.max(y)/ybinwidth) * ybinwidth + ybinwidth
    xmax = int(np.max(x)/xbinwidth) * xbinwidth + xbinwidth

    ybins = np.arange(ymin, ymax, ybinwidth)
    xbins = np.arange(xmin, xmax, xbinwidth)

    divider = make_axes_locatable(ax)

    axr = divider.append_axes("right", 2.5, pad=0.5, sharey=ax)
    axt = divider.append_axes("top", 2.5, pad=0.4, sharex=ax)

    bins = axr.hist(y, bins=ybins, orientation='horizontal', weights=np.ones(len(y)) / len(y), rwidth=0.8)
    bins = axt.hist(x, bins=xbins, orientation='vertical', weights=np.ones(len(x)) / len(x), rwidth=0.8)

    return fig

def plot_scatter_joint(dataset, x, y):
    fig, ax = plt.subplots(figsize=(18, 15))

    sns.jointplot(x='E eff', y='rmse', data=result, ax=ax)

    return fig

def plot_curves(curves, index, cols_source, cols_target, cols_predict):
    fig_count = len(curves)

    fig, axes = plt.subplots(nrows=int(fig_count/2), 
                             ncols=2, 
                             figsize=(18, fig_count*3), 
                             sharey=True, 
                             sharex=False)
    ax = 0
    for _, row in curves.iterrows():
        
        axis = axes[int(ax/2)][ax%2]

        df = pd.DataFrame(index=index)
        #df['source'] = row[cols_source].values
        df['target'] = row[cols_target].values
        df['predict'] = row[cols_predict].values
        
        df.plot(marker='.', ax = axis, ylim=(0, 1), linewidth=2, markersize=10)
        
        ax += 1
    
    return fig
