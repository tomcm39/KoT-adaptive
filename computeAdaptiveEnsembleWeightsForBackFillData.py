#mcandrew

import argparse
import sys
sys.path.append('./_0_mixtureModelAlgorithms/')

import numpy as np
import pandas as pd

from deviMM import *

def timeStamp():
    import datetime
    return datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

def removeEnsembleModels(d):
    excludedModels = pd.read_csv('./excludedModels/excludedModels.csv')
    d = d.merge(excludedModels, left_on='model',right_on='model')
    d = d.loc[d.excluded==0,:]
    return d

def countNumOfExcludedModels():
    excludedModels = pd.read_csv('./excludedModels/excludedModels.csv')
    return excludedModels.excluded.sum()

def createListOfExcludedModels():
    excludedModels = pd.read_csv('./excludedModels/excludedModels.csv')
    return list(excludedModels.loc[excludedModels.excluded==1,'model'])

def countNumberOfUniqueModels(d):
    return len(d.model.unique())

def removeSeason(d,s):
    return d.loc[d.Season!=s,:]

def subsetTestSet2SpecificRegionTarget(d,r,t):
    return d.loc[(d.Target==t) & (d.Location==r),:]

def keepLogScoresAndTranspose(d):
    d = d.reset_index()
    d = pd.pivot_table(data = d
                       ,columns = ['model']
                       ,values  = ['logScore']
                       ,index   = ['region','target','surveillanceWeek']
    )
    models = [y for (x,y) in d.columns]
    return pd.DataFrame(np.matrix(d.values), columns = models)

def removeNALogScores(d):
    modelNames = d.columns 
    modelPis = {name:0. for name in modelNames}

    logScoreDataNoNA  = d.dropna(1)
    modelNamesNoNA = logScoreDataNoNA.columns
    return logScoreDataNoNA,modelNames,modelNamesNoNA

def capLogScoresAtNeg10(d):
    d.loc[d.logScore<-10,'Score']=-10.
    return d

def trainRegularizedStaticEnsemble(d,PRIOR):
    numberOfObservations, numberOfModels = d.shape
    priorWeightPerModel  = PRIOR*numberOfObservations/numberOfModels
    
    alphas,elbos =  deviMM(d.as_matrix()
                           ,priorPis = np.array(numberOfModels*[priorWeightPerModel])
                           ,maxIters = 10**2
                           ,relDiffThreshold = -1)
    return alphas


def computeAdaptiveWeights(singleBinLogScores):

    data = {'component_model_id':[],'weight':[]}
    if singleBinLogScores.shape[0]==0:
        excludedModels = set(createListOfExcludedModels())
        modelNames = list( set(pd.read_csv('./forecasts/fluSightForecasts.csv').model.unique()) - excludedModels)
        modelNamesNoNA = modelNames
        numberOfModels = len(modelNames)
        pis = [1./numberOfModels for x in range(numberOfModels)]
    else:
        numberOfModels = countNumberOfUniqueModels(singleBinLogScores)
        priorPercent = float(0.10)

        allRegionTargetData = singleBinLogScores
        allRegionTargetData = capLogScoresAtNeg10(allRegionTargetData) 
        logScoreData        = keepLogScoresAndTranspose(allRegionTargetData) 

        logScoreData, modelNames, modelNamesNoNA = removeNALogScores(logScoreData)
        
        alphas = trainRegularizedStaticEnsemble(logScoreData,priorPercent)
        pis = alphas/sum(alphas)

    for (model,pi) in zip(modelNamesNoNA, pis):
        data['component_model_id'].append(model)
        data['weight'].append(float(pi))

    for model in modelNames:
        if model in data['component_model_id']:
            continue
        data['component_model_id'].append(model)
        data['weight'].append(0.)

    excludedModels = createListOfExcludedModels()
    for model in excludedModels:
        data['component_model_id'].append(model)
        data['weight'].append(0.)
        
    data = pd.DataFrame(data)
    return data

def grabForecastWeeks():
    return [int(x) for x in sorted(pd.read_csv('forecasts/fluSightForecasts.csv')['EW'].unique())]

if __name__ == "__main__":

    singleBinLogScores = pd.read_csv('./backFillScores/logScores.csv')
    singleBinLogScores = removeEnsembleModels(singleBinLogScores)

    allWts = pd.DataFrame()
    for forecastWeek in grabForecastWeeks():
        sys.stdout.write('\rForecast Week = {:d}\r'.format(forecastWeek))
        sys.stdout.flush()
        logScores = singleBinLogScores[singleBinLogScores.releaseEW==forecastWeek]
        
        weights = computeAdaptiveWeights(logScores)
        weights['forecastWeek'] = forecastWeek

        allWts = allWts.append(weights)
        
    allWts.to_csv('./historicalWeightsBackfill/adaptive-regularized-ensemble-constant_{:s}.csv'.format(timeStamp()),index=False)
    allWts.to_csv('./weightsBackFill/adaptive-regularized-ensemble-constant.csv',index=False)
