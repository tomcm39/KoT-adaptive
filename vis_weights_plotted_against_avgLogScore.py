#mcandrew

import sys
import pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def averageLogScoreByModel(d):
    return d.groupby(['model']).apply(lambda x: pd.Series({'avgLogScore':np.mean(x.logScore)})).reset_index()

def findMostRecentEW(d):
    return max(d.surveillanceWeek)

def defineEqualWeight(d):
    return 1./len(weightAndScores.model.unique())

def mm2inch(x):
    return x/25.4

def orderModels(d):
    d = d.sort_values('weight')
    return d.model


if __name__ == "__main__":

    scores       = pd.read_csv('./scores/logScores.csv')
    mostRecentEW = findMostRecentEW(scores)
    
    averageScores = averageLogScoreByModel(scores)
    
    weights = pd.read_csv('./weights/adaptive-regularized-ensemble-constant.csv')

    weightAndScores = weights.merge(averageScores, left_on = ['component_model_id'],right_on=['model'])
    weightAndScores = weightAndScores[weightAndScores.weight>0]

    equalWeight = defineEqualWeight(weightAndScores)
    weightAndScores['relWeight'] = weightAndScores.weight/equalWeight

    highest2SmallestWeights = orderModels(weightAndScores)
    
    fig,ax = plt.subplots()
    ax.plot(weightAndScores.weight,weightAndScores.avgLogScore,'ko',alpha=0.80)

    for (idx,row) in weightAndScores.iterrows():
        ax.text( row['weight'], row['avgLogScore']*1.05, row['model'], fontsize=8.0,rotation=90,ha='center',va='top' )
   
    ax.set_xlabel('KoT-adaptive ensemble weights')
    ax.set_ylabel('Mean logscore')
    
    fig.set_size_inches(mm2inch(183),mm2inch(183))
    fig.set_tight_layout(True)
    plt.savefig('./vis/weights_vs_avgLogScore_EW{:d}.pdf'.format(mostRecentEW))
    plt.close()
