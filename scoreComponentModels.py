#mcandrew

import sys
import numpy as np
import pandas as pd

from epiweeks import Week, Year

def computeTargetILIepiWeek(forecastWeek,weekAhead):
    iliYear,iliWeek = int(str(forecastWeek)[:3+1]),int(str(forecastWeek)[4:])
    iliEW = Week(iliYear,iliWeek)-2 + int(weekAhead)
    iliEW = int("{:04d}{:02d}".format(iliEW.year,iliEW.week))
    return iliEW

def removePointForecasts(forecasts):
    forecasts = forecasts.loc[forecasts.type!='Point',:]
    return forecasts

def subsetAllForecasts2WeekAheadTargets(forecasts):
    weekAheadForecasts = forecasts.loc[ forecasts.target.str.contains('ahead'),: ]
    weekAheadForecasts.bin_start_incl  = weekAheadForecasts.bin_start_incl.astype(float)
    weekAheadForecasts.bin_end_notincl = weekAheadForecasts.bin_end_notincl.astype(float)
    return weekAheadForecasts

def computeLogScores(forecastsAndILI):
        subsetToProbabilities = forecastsAndILI.loc[  (forecastsAndILI.bin_start_incl <= forecastsAndILI.wili)
                                                    & (forecastsAndILI.bin_end_notincl > forecastsAndILI.wili),: ]
        subsetToProbabilities['logScore'] = np.log(subsetToProbabilities.value)
        logScores = subsetToProbabilities.loc[:,['model','location','target','region','logScore']]
        logScores['surveillanceWeek'] = forecastWeek
        logScores['targetWeek']       = iliEW 
        return logScores

if __name__ == "__main__":

    iliData   = pd.read_csv('./data/epiData.csv')
    forecasts = pd.read_csv('./forecasts/fluSightForecasts.csv')
    forecasts = removePointForecasts(forecasts)

    epiWeeksWithData   = iliData.EW.unique()
    forecastedEpiWeeks = forecasts.EW.unique()
    
    # week aheads 
    weekAheadForecasts = subsetAllForecasts2WeekAheadTargets(forecasts)
    
    allLogScores = pd.DataFrame()
    for forecastWeek in forecastedEpiWeeks:
        
        for weekAhead in np.arange(1,4+1):
            weekSubset       = weekAheadForecasts.target=='{:d} wk ahead'.format(weekAhead)
            forecastEWSubset = weekAheadForecasts.EW == forecastWeek
            
            forecastsForSingleWeekAheadTarget = weekAheadForecasts.loc[(weekSubset & forecastEWSubset),:]

            iliEW = computeTargetILIepiWeek(forecastWeek,weekAhead)
            iliDataForEW = iliData.loc[iliData.EW==iliEW,:]
            
            forecastsAndILI = forecastsForSingleWeekAheadTarget.merge( iliDataForEW, left_on = ['location'], right_on=['region']   )

            logScores = computeLogScores(forecastsAndILI)
            allLogScores = allLogScores.append(logScores)

    allLogScores.to_csv('./historicalScores/allLogScores_{:s}.csv'.format(timeStamp()),index=False)
    allLogScores.to_csv('./scores/logScores.csv',index=False)
