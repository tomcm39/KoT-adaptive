#mcandrew

import sys
import numpy as np
import pandas as pd
import datetime

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
    
    return d.loc[:,['Location','Target','Type','Unit','Bin_start_incl','Bin_end_notincl','Value']  ]

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

def captureSubmissionInformation(mostRecentSurviellanceWeek):
    EW = int(str(mostRecentSurviellanceWeek)[4:])
    today = datetime.datetime.today()
    year,month,day  = today.year,today.month,today.day
    return EW,year,month,day

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

def removeHashValueFromValues(forecastsAndWeights):
    forecastsAndWeights['value'] = [ np.nan if x=='#VALUE!' else float(x) for x in forecastsAndWeights.value]
    return forecastsAndWeights

if __name__ == "__main__":

    forecasts = pd.read_csv('./forecasts/fluSightForecasts.csv') 
    forecasts = formatBins(forecasts)
    
    weights   = pd.read_csv('./weights/adaptive-regularized-ensemble-constant.csv')

    mostRecentSurviellanceWeek = 201945
    forecastsAndWeights = forecasts.merge(weights, left_on=['model'],right_on=['component_model_id']) 

    try:
        forecastsAndWeights = cap2MostRecentSurvWeek(forecastsAndWeights,mostRecentSurviellanceWeek)
    except NameError:
        mostRecentSurviellanceWeek = computeMostRecentSurvWeek()
        forecastsAndWeights = cap2MostRecentSurvWeek(forecastsAndWeights,mostRecentSurviellanceWeek)
            
    forecastsAndWeights = renormalizeWeightsForModelsThatDontSubmit(forecastsAndWeights) 
    
    forecastsAndWeights = removeHashValueFromValues(forecastsAndWeights)
    forecastsAndWeights.value = forecastsAndWeights.value.astype(float)
    forecastsAndWeights['ensembleForecast'] = forecastsAndWeights.weight*forecastsAndWeights.value
    forecastsAndWeights = forecastsAndWeights.groupby(['location','target','type','unit','bin_start_incl','bin_end_notincl']).apply( lambda x: pd.Series({'ensembleForecast':x.ensembleForecast.sum()}) ).reset_index()
    
    ensembleForecast = formatEnsembleForecast(forecastsAndWeights)
    ensembleForecast = sortEnsembleForecast(ensembleForecast)

    EW,year,month,day = captureSubmissionInformation(mostRecentSurviellanceWeek)
    ensembleForecast.to_csv('./ensembleForecasts/EW{:02d}-KoT-adaptive-{:d}-{:d}-{:d}.csv'.format(EW,year,month,day),index=False)
    ensembleForecast.to_csv('./historicalEnsembleForecasts/EW{:02d}-KoT-adaptive-{:d}-{:d}-{:d}.csv'.format(EW,year,month,day),index=False)
