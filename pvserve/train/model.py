import pandas as pd

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras import optimizers
from tensorflow.keras import backend as K 


def __get_optimizer(optimizer, lr):
    if optimizer == 'sgd':
        return optimizers.SGD(lr=lr)
    elif optimizer == 'rmsprop':
        return optimizers.RMSprop(lr=lr)
    elif optimizer == 'adagrad':
        return optimizers.Adagrad(lr=lr)
    elif optimizer == 'adadelta':
        return optimizers.Adadelta(lr=lr)
    elif optimizer == 'adam':
        return optimizers.Adam(lr=lr)
    elif optimizer == 'adamax':
        return optimizers.Adamax(lr=lr)
    elif optimizer == 'nadam':
        return optimizers.Nadam(lr=lr)

def model_build(input_size, 
          output_size, 
          hidden_layer, 
          neuron_factor, 
          activation='tanh', 
          optimizer='rmsprop',
          lr=0.001,
          loss='mse', 
          metrics=['accuracy']):

    K.clear_session()

    optimizer = __get_optimizer(optimizer, lr)
    
    neurons_per_layer = int(input_size * neuron_factor)

    model = Sequential()
    model.add(Dense(neurons_per_layer, activation=activation, input_shape=(input_size,)))

    for i in range(0, hidden_layer):
        model.add(Dense(neurons_per_layer, activation=activation))
        model.add(Dropout(0.3))

    model.add(Dense(output_size, activation=activation))
    model.compile(loss=loss, optimizer=optimizer, metrics=metrics)

    return model

def model_fit(model, x, y, validation, epochs, batch_size, verbose=1):
    result = model.fit(x, y, 
                       validation_data=validation, 
                       epochs=epochs, 
                       batch_size=batch_size, 
                       verbose=verbose)

    return pd.DataFrame(data=result.history)

def model_evaluate(model, x, y, verbose=1):
    return model.evaluate(x, y, verbose=verbose)

def model_predict(model, x, columns):
    result = model.predict(x.values)

    return pd.DataFrame(index=x.index, columns=columns, data=result)