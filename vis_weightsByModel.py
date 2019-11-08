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
    bp = sns.barplot(  y='model'
                      ,x='relWeight'
                      ,color="0.6"
                      ,order =  highest2SmallestWeights
                      ,data=weightAndScores,ax=ax)
    ylims = ax.get_ylim()
    ax.plot([1.0,1.0],ax.get_ylim(),'k-')
    ax.set_ylim(ylims)
    
    ax.set_xlabel(r'Relative weight = Weight / Equal Weight')
    ax.set_ylabel('')
    fig.set_size_inches(mm2inch(183),mm2inch(183))
    fig.set_tight_layout(True)
    plt.savefig('./vis/barplotOfWeights_EW{:d}.pdf'.format(mostRecentEW))
    plt.close()
