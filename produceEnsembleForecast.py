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

def captureSubmissionInformation(mostRecentSurviellanceWeek):
    EW = int(str(mostRecentSurviellanceWeek)[4:])
    today = datetime.datetime.today()
    year,month,day  = today.year,today.month,today.day
    return EW,year,month,day

if __name__ == "__main__":

    forecasts = pd.read_csv('./forecasts/fluSightForecasts.csv') 
    forecasts = formatBins(forecasts)
    
    weights   = pd.read_csv('./weights/adaptive-regularized-ensemble-constant.csv')

    mostRecentSurviellanceWeek = computeMostRecentSurvWeek()

    forecastsAndWeights = forecasts.merge(weights, left_on=['model'],right_on=['component_model_id']) 
    forecastsAndWeights = cap2MostRecentSurvWeek(forecastsAndWeights,mostRecentSurviellanceWeek)

    forecastsAndWeights['ensembleForecast'] = forecastsAndWeights.weight*forecastsAndWeights.value
    forecastsAndWeights = forecastsAndWeights.groupby(['location','target','type','unit','bin_start_incl','bin_end_notincl']).apply( lambda x: pd.Series({'ensembleForecast':x.ensembleForecast.sum()}) ).reset_index()
    
    ensembleForecast = formatEnsembleForecast(forecastsAndWeights)

    EW,year,month,day = captureSubmissionInformation(mostRecentSurviellanceWeek)
    ensembleForecast.to_csv('./ensembleForecasts/EW{:02d}-KoT-adaptive-{:d}-{:d}-{:d}.csv'.format(EW,year,month,day),index=False)
    ensembleForecast.to_csv('./historicalEnsembleForecasts/EW{:02d}-KoT-adaptive-{:d}-{:d}-{:d}.csv'.format(EW,year,month,day),index=False)
