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

def timeStamp():
    return datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

if __name__ == "__main__":

    firstWeekOfSeason = datetime.datetime.strptime('2019-10-01',"%Y-%m-%d")
    epiWeeks = computeEpiWeeksWithData(firstWeekOfSeason)
    regions = createAllRegions()
    
    fluData = Epidata.fluview(regions = regions ,epiweeks = epiWeeks)
    if fluData['message'] != 'success':
        print('could not download data')
        sys.exit()

    mostRecentEpiData = {'EW':[],'region':[],'wili':[]}
    for data in fluData['epidata']:
        mostRecentEpiData['EW'].append(data['epiweek'])
        mostRecentEpiData['region'].append(data['region'])
        mostRecentEpiData['wili'].append(data['wili'])
    mostRecentEpiData = pd.DataFrame(mostRecentEpiData)
    
    mostRecentEpiData.to_csv('./historicalData/epiData_{:s}.csv'.format(timeStamp()),index=False)
    mostRecentEpiData.to_csv('./data/epiData.csv',index=False)
