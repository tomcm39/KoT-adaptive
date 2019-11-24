#mcandrew

import sys
import numpy as np
import pandas as pd

from epiweeks import Week, Year

def timeStamp():
    import datetime
    return datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

def computeTargetILIepiWeek(forecastWeek,weekAhead):
    iliYear,iliWeek = int(str(forecastWeek)[:3+1]),int(str(forecastWeek)[4:])
    iliEW = Week(iliYear,iliWeek) + int(weekAhead)
    iliEW = int("{:04d}{:02d}".format(iliEW.year,iliEW.week))
    return iliEW

def removePointForecasts(forecasts):
    forecasts = forecasts.loc[forecasts.type!='Point',:]
    return forecasts

def removeExtraneousExtraRows(forecasts):
   forecasts = forecasts.loc[ ~pd.isna(forecasts.bin_start_incl),:]   
   return forecasts

def subsetAllForecasts2WeekAheadTargets(forecasts):
    weekAheadForecasts = forecasts.loc[ forecasts.target.str.contains('ahead'),: ]
    weekAheadForecasts.bin_start_incl  = weekAheadForecasts.bin_start_incl.astype(float)
    weekAheadForecasts.bin_end_notincl = weekAheadForecasts.bin_end_notincl.astype(float)
    return weekAheadForecasts

def computeLogScores(forecastsAndILI,forecastWeek,iliEW):
    if forecastsAndILI.shape[0]==0:
        return pd.DataFrame()
    
    from datetime import datetime
    calendarEW = Week.thisweek()
    dayOfWeek  = datetime.today().weekday
    if dayOfWeek in {5,6}: # Saturday or Sunday
        calendarWeek = "{:d}{:d}".format(calendarEW.year,calendarEW.week+1) # should be referenced from the next week
    else:
        calendarWeek = "{:d}{:d}".format(calendarEW.year,calendarEW.week)

    subsetToProbabilities = forecastsAndILI.loc[  (forecastsAndILI.bin_start_incl <= forecastsAndILI.wili)
                                                  & (forecastsAndILI.bin_end_notincl > forecastsAndILI.wili),: ]
    subsetToProbabilities['logScore'] = np.log([float(x) for x in subsetToProbabilities.value])
    logScores = subsetToProbabilities.loc[:,['model','location','target','region','lag','releaseEW','releaseDate','wili','logScore']]
    logScores['surveillanceWeek'] = forecastWeek  # this is the most recent week of data available
    logScores['calendarWeek']     = calendarWeek  # this is the present week in real-time
    logScores['targetWeek']       = iliEW         # this is the target week of forecasting
    
    return logScores

if __name__ == "__main__":

    iliData   = pd.read_csv('./backfilldata/epiData.csv')

    forecasts = pd.read_csv('./forecasts/fluSightForecasts.csv')
    forecasts = removePointForecasts(forecasts)
    forecasts = removeExtraneousExtraRows(forecasts)
    weekAheadForecasts = subsetAllForecasts2WeekAheadTargets(forecasts)

    forecastedEpiWeeks = sorted(forecasts.EW.astype(int).unique())

    epiWeeksWithData   = iliData.EW.unique()
    surveillanceWeeks = sorted(iliData.surveillanceWeek.unique())
   
    allLogScores = pd.DataFrame()
    for surveillanceWeek in surveillanceWeeks:
        sys.stdout.write('\r{:d}\r'.format(surveillanceWeek))
        sys.stdout.flush()
        ewIliData = iliData[iliData.surveillanceWeek==surveillanceWeek]

        for forecastWeek in forecastedEpiWeeks:
            for weekAhead in np.arange(1,4+1):
                weekSubset       = weekAheadForecasts.target=='{:d} wk ahead'.format(weekAhead)
                forecastEWSubset = weekAheadForecasts.EW == forecastWeek

                forecastsForSingleWeekAheadTarget = weekAheadForecasts.loc[(weekSubset & forecastEWSubset),:]

                iliEW = computeTargetILIepiWeek(forecastWeek,weekAhead)
                iliDataForEW = ewIliData.loc[ewIliData.EW==iliEW,:]

                forecastsAndILI = forecastsForSingleWeekAheadTarget.merge( iliDataForEW, left_on = ['location'], right_on=['region'])

                logScores = computeLogScores(forecastsAndILI,forecastWeek,iliEW)
                
                allLogScores = allLogScores.append(logScores)

    allLogScores = allLogScores.replace(-np.Inf,-10.0)

    allLogScores.to_csv('./historicalBackfillScores/allLogScores_{:s}.csv'.format(timeStamp()),index=False)
    allLogScores.to_csv('./backFillScores/logScores.csv',index=False)
