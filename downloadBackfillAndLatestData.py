#mcandrew

import sys
import numpy as np
import pandas as pd

from delphi_epidata import Epidata
from epiweeks import Week, Year
import datetime

def fromDateTime2EW(dt):
    w = Week.fromdate(dt.year,dt.month,dt.day)
    return "{:4}{:2}".format(w.year,w.week)

def createAllRegions():
    return ['nat'] + [ 'HHS{:d}'.format(n) for n in np.arange(1,10+1)]

def computeEpiWeeksWithData(firstWeekOfSeason):
    thisWeek  = datetime.datetime.today() 
    _1Week    = datetime.timedelta(days=7)

    week    = firstWeekOfSeason
    epiWeeks = [fromDateTime2EW(firstWeekOfSeason)]
    while week<thisWeek:
        week = week + _1Week
        epiWeeks.append(fromDateTime2EW(week))
    epiWeeks = epiWeeks[:-2] # ILINET is 2 weeks behind the current Epidemic Week.
    return epiWeeks

def addSurveillanceWeeks(d):
    unique_EWLagPairs = d.loc[:,['EW','lag']].drop_duplicates()
    def addLag(obs):
        EW = str(obs.EW)
        lag = int(obs.lag)
        yr,wk = int(EW[:4]),int(EW[4:])
        surveillanceWeek = Week(yr,wk) + lag
        obs['surveillanceWeek'] = "{:d}{:d}".format(surveillanceWeek.year,surveillanceWeek.week)
        return obs
    unique_EWLagPairs= unique_EWLagPairs.apply(addLag,1)
    return d.merge( unique_EWLagPairs, on = ['EW','lag'])

def timeStamp():
    return datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

if __name__ == "__main__":

    firstWeekOfSeason = datetime.datetime.strptime('2019-10-01',"%Y-%m-%d")
    epiWeeks = computeEpiWeeksWithData(firstWeekOfSeason)
    regions = createAllRegions()
    
    mostRecentEpiData = {'EW':[],'region':[],'wili':[],'lag':[],'releaseDate':[],'releaseEW':[]}
    for lag in np.arange(40,-1,-1):
        fluData = Epidata.fluview(regions = regions ,epiweeks = epiWeeks,lag=lag)
        if fluData['message'] != 'success':
            print('could not download data-lag={:d}'.format(lag))
            continue
        print('Downloading data-lag={:d}'.format(lag))
        for data in fluData['epidata']:
            mostRecentEpiData['EW'].append(data['epiweek'])
            mostRecentEpiData['region'].append(data['region'])
            mostRecentEpiData['wili'].append(data['wili'])
            mostRecentEpiData['lag'].append(lag)
            mostRecentEpiData['releaseDate'].append(data['release_date'])

            releasedateDT = datetime.datetime.strptime(data['release_date'],"%Y-%m-%d")
            mostRecentEpiData['releaseEW'].append( fromDateTime2EW(releasedateDT ))
            
    mostRecentEpiData = pd.DataFrame(mostRecentEpiData)
    mostRecentEpiData = addSurveillanceWeeks(mostRecentEpiData)

    mostRecentEpiData.to_csv('./historicalBackfillData/epiData_{:s}.csv'.format(timeStamp()),index=False)
    mostRecentEpiData.to_csv('./backfillData/epiData.csv',index=False)
