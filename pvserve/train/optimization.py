import pandas as pd
import numpy as np
import random, sys

STATUSBAR_SIZE = 30

def optimize_combine(params):
    combined = None
    for param in params:
        tmp = pd.DataFrame(columns=[param], data=params[param])
        tmp['key'] = 0
        
        if combined is None:
            combined = tmp
        else:
            combined = combined.merge(tmp, on='key')

    combined = combined.drop("key", axis=1)

    return combined

def optimize_match(remaining, values):
    i=0
    for val in values:
        if val is not None:
            remaining = remaining[remaining.iloc[:,i] == val]
        i += 1

    return remaining

def optimize_populate(remaining, population, pop_size):
    if len(population) == 0:
        raise ValueError

    # recombination
    for i in range(0, len(population) - 1):
        p0 = population.iloc[i]
        p1 = population.iloc[i + 1]

        c0 = np.concatenate((p0[:int(len(p0)/2)], p1[int(len(p1)/2):])) 
        c1 = np.concatenate((p1[:int(len(p1)/2)], p0[int(len(p0)/2):])) 

        c0 = optimize_match(remaining, c0)
        population = population.append(c0)
        remaining = remaining.drop(index=c0.index)


        c1 = optimize_match(remaining, c1)
        population = population.append(c1)
        remaining = remaining.drop(index=c1.index)

    # mutation
    while len(population) < pop_size:
        mask = population.sample(1).values[0]

        mask[random.randint(0, len(mask)-1)] = None
        individuals = optimize_match(remaining, mask)

        if len(individuals) > 0:
            individuel = individuals.sample(1)
            population = population.append(individuel)
            remaining = remaining.drop(index=individuel.index)

    return population


def optimize_run(params, init_epoch, score_fn, epochs=8, pop_size=10, parents=0.4, minimize_score=True):
    remaining = optimize_combine(params)
    history = remaining.copy()
    history['score'] = np.nan
    history['epoch'] = np.nan

    print("Total cominations: {}".format(len(remaining)))

    best = optimize_match(remaining, init_epoch)
    remaining = remaining.drop(index=best.index)

    epoch = 0
    while epoch < epochs:
        print("Epoch {}/{}".format(epoch+1, epochs))

        population = optimize_populate(remaining, best, pop_size)
        remaining = remaining.drop(index=population.index, errors='ignore')

        n = 0
        for i, row in population.iterrows():
            progress = int((n / pop_size) * STATUSBAR_SIZE)
            sys.stdout.write("\r{:03d}/{:03d} [{}{}]        Params:{:>50}".format(n+1, pop_size, (progress * '='), ((STATUSBAR_SIZE - progress) * '-'), str(row.values)))
            sys.stdout.flush()

            score = history.loc[i, 'score']
            if np.isnan(score):
                score = score_fn(*row.values)
                history.loc[i, 'score'] = score
                history.loc[i, 'epoch'] = epoch + 1

            n += 1
        
        history = history.sort_values(by=['score'], ascending=minimize_score)
        
        sys.stdout.write("\r{:03d}/{:03d} [{}]    Top Params:{:>50}\n".format(pop_size, pop_size, STATUSBAR_SIZE*'=', str(history.head(1).values[0][:-2])))
        sys.stdout.flush()

        best = history.head(int(pop_size * parents)).drop(columns=['score', 'epoch'])

        epoch += 1

    return history[~np.isnan(history.epoch)]



