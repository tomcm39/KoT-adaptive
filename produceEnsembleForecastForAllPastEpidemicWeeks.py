#mcandrew

import sys
import numpy as np
import pandas as pd
import datetime

# COMPUTE WEIGHTS

sys.path.append('./_0_mixtureModelAlgorithms/')

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
    return logScoreDataNoNA,modelNamesNoNA

def capLogScoresAtNeg10(d):
    d.loc[d.logScore<-10,'Score']=-10.
    return d

def trainRegularizedAdaptEnsemble(d,PRIOR):
    numberOfObservations, numberOfModels = d.shape
    priorWeightPerModel  = PRIOR*numberOfObservations/numberOfModels
    
    alphas,elbos =  deviMM(d.as_matrix()
                           ,priorPis = np.array(numberOfModels*[priorWeightPerModel])
                           ,maxIters = 10**2
                           ,relDiffThreshold = -1)
    return alphas

def removeEnsembleModels(d):
    excludedModels = pd.read_csv('./excludedModels/excludedModels.csv')
    d = d.merge(excludedModels, left_on='model',right_on='model')
    d = d.loc[d.excluded==0,:]
    return d

def computeKoTadaptiveWeights(singleBinLogScores):
    data = {'component_model_id':[],'weight':[]}

    if singleBinLogScores.shape[0]==0:
        excludedModels = set(createListOfExcludedModels())
        modelNames = list( set(pd.read_csv('./forecasts/fluSightForecasts.csv').model.unique()) - excludedModels)
        numberOfModels = len(modelNames)
        pis = [1./numberOfModels for x in range(numberOfModels)]
    else:
        numberOfModels = countNumberOfUniqueModels(singleBinLogScores)
        priorPercent = float(0.10)

        allRegionTargetData = singleBinLogScores
        allRegionTargetData = capLogScoresAtNeg10(allRegionTargetData) 
        logScoreData        = keepLogScoresAndTranspose(allRegionTargetData) 

        logScoreData, modelNames = removeNALogScores(logScoreData)

        alphas = trainRegularizedAdaptEnsemble(logScoreData,priorPercent)
        pis = alphas/sum(alphas)

    for (model,pi) in zip(modelNames, pis):
        data['component_model_id'].append(model)
        data['weight'].append(float(pi))

    excludedModels = createListOfExcludedModels()
    for model in excludedModels:
        data['component_model_id'].append(model)
        data['weight'].append(0.)
        
    data = pd.DataFrame(data)
    return data
#---------------------------------------------------------------------------

def computeMostRecentSurvWeek():
        return pd.read_csv('./data/epiData.csv').EW.max()

def cap2MostRecentSurvWeek(d,MRW):
    return d.loc[d.EW==MRW,:]

def formatBins(d):
    reformatted = [] 
    for x in d.loc[:,'bin_start_incl']:
        try:
            reformatted.append(float(x))
        except:
            reformatted.append(x)
    d.loc[:,'bin_start_incl'] = [str(x) for x in reformatted]

    reformatted = []
    for x in d.loc[:,'bin_end_notincl']:
        try:
            reformatted.append(float(x))
        except:
            reformatted.append(x)
    d.loc[:,'bin_end_notincl'] = [str(x) for x in reformatted]
    return d
    
def formatEnsembleForecast(d):

    d = d.rename(columns = {'location':'Location'
                            ,'target':'Target'
                            ,'type':'Type'
                            ,'unit':'Unit'
                            ,'bin_start_incl':'Bin_start_incl'
                            ,'bin_end_notincl':'Bin_end_notincl' })
    d['Value'] = d['ensembleForecast']

    d.loc[d.Location=='nat','Location'] = 'US National'
    for n in np.arange(1,10+1):
        d.loc[d.Location=='hhs{:d}'.format(n),'Location'] = 'HHS Region {:d}'.format(n)
    
    return d.loc[:,['EW','Location','Target','Type','Unit','Bin_start_incl','Bin_end_notincl','Value']  ]

def renormalizeWeightsForModelsThatDontSubmit(d):
        subsetModelsWeights = d.loc[:,['model','weight']].drop_duplicates()

        print("Sum of weights before renorm = {:f}".format(subsetModelsWeights.weight.sum()))
        
        subsetModelsWeights = subsetModelsWeights.rename(columns={'weight':'renormWeight'})
        
        sumWeights = subsetModelsWeights.renormWeight.sum()
        subsetModelsWeights['renormWeight'] = subsetModelsWeights.renormWeight/sumWeights
        
        d = d.merge(subsetModelsWeights, left_on=['model'], right_on=['model'])
        d = d.drop(columns = ['weight'])
        d = d.rename(columns = {'renormWeight':'weight'})

        print("Sum of weights after renorm = {:f}".format(d.loc[:,['model','weight']].drop_duplicates().weight.sum()))
        
        return d

def captureSubmissionInformation(mostRecentSurviellanceWeek):
    EW = int(str(mostRecentSurviellanceWeek)[4:])
    today = datetime.datetime.today()
    year,month,day  = today.year,today.month,today.day
    return EW,year,month,day

def reformatValueColumn(forecastsAndWeights):
    reformattedValue = []
    for x in forecastsAndWeights.value:
        try:
            reformattedValue.append(float(x))
        except ValueError:
            reformattedValue.append(-np.inf)
    forecastsAndWeights['value'] = reformattedValue
    return forecastsAndWeights

def sortEnsembleForecast(d):
        
    leftBin = []
    for x in d.Bin_start_incl:
        if x=='none':
            leftBin.append(-1.)
        else:
            leftBin.append(float(x))
    d['Bin_start_incl'] = leftBin

    rightBin = []
    for x in d.Bin_end_notincl:
        if x=='none':
            rightBin.append(-2.)
        else:
            rightBin.append(float(x))
    d['Bin_end_notincl'] = rightBin
    
    d['Bin_start_incl']  = d.Bin_start_incl.astype(float)
    d['Bin_end_notincl'] = d.Bin_end_notincl.astype(float)
    d = d.sort_values(['Location','Target','Type','Bin_start_incl','Bin_end_notincl'])

    d['Bin_start_incl'] = d.Bin_start_incl.astype(str)
    d['Bin_end_notincl'] = d.Bin_end_notincl.astype(str)
    
    d.loc[d.Bin_start_incl =='-1','Bin_start_incl']  = 'none'
    d.loc[d.Bin_end_notincl=='-2','Bin_end_notincl'] = 'none'
        
    return d

def grabForecastWeeks(forecasts):
     weeks = [int(x) for x in sorted(forecasts['EW'].unique())]
     return weeks

def transformFWeek2WeightWeek(forecastWeek):
    from epiweeks import Week
    year,week = int(str(forecastWeek)[:4]), int(str(forecastWeek)[4:])
    week = Week(year,week)+2
    return int("{:04d}{:02d}".format(week.year,week.week))

 
if __name__ == "__main__":

    forecasts = pd.read_csv('./forecasts/flusightforecasts.csv')
    forecasts = formatBins(forecasts)
    
    allWts = pd.read_csv('./weightsBackfill/adaptive-regularized-ensemble-constant.csv')
    
    forecastWeeks = grabForecastWeeks(forecasts)
    allEnsembleForecasts = pd.DataFrame()
    for (weekNum,forecastWeek) in enumerate(forecastWeeks):
        sys.stdout.write('\r{:d}\r'.format(forecastWeek))
        sys.stdout.flush()

        ew_forecasts = forecasts.loc[forecasts.EW==forecastWeek,:]
        if ew_forecasts.shape[0]==0:
            print('No forecast data for EW = {:d}'.format(forecastWeek))
            continue
        
        weights = allWts[allWts.forecastWeek== transformFWeek2WeightWeek(forecastWeek)]
   
        forecastsAndWeights = ew_forecasts.merge(weights, left_on=['model'],right_on=['component_model_id'])
        forecastsAndWeights = reformatValueColumn(forecastsAndWeights)
    
        forecastsAndWeights = renormalizeWeightsForModelsThatDontSubmit(forecastsAndWeights) 

        forecastsAndWeights.value = forecastsAndWeights.value.astype(float)
        forecastsAndWeights['ensembleForecast'] = forecastsAndWeights.weight*forecastsAndWeights.value
        forecastsAndWeights = forecastsAndWeights.groupby(['EW','location','target','type','unit','bin_start_incl','bin_end_notincl']).apply( lambda x: pd.Series({'ensembleForecast':x.ensembleForecast.sum()}) ).reset_index()
    
        ensembleForecast = formatEnsembleForecast(forecastsAndWeights)
        ensembleForecast['forecastWeek'] = forecastWeek
        ensembleForecast = sortEnsembleForecast(ensembleForecast)

        allEnsembleForecasts = allEnsembleForecasts.append(ensembleForecast)

    mostRecentSurviellanceWeek = computeMostRecentSurvWeek()
    EW,year,month,day = captureSubmissionInformation(mostRecentSurviellanceWeek)
    allEnsembleForecasts.to_csv('./ensembleForecastsForBackfill/EW{:02d}-KoT-adaptive-{:d}-{:d}-{:d}.csv'.format(EW,year,month,day),index=False)
    allEnsembleForecasts.to_csv('./historicalEnsembleForecastsForBackfill/EW{:02d}-KoT-adaptive-{:d}-{:d}-{:d}.csv'.format(EW,year,month,day),index=False)
