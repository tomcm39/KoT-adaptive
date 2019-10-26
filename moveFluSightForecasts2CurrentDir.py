#mcandrew

import os
import sys
import numpy as np
import pandas as pd
from glob import glob

def grabEW(f,yearSeasonStarted):
    import re
    EWXX = int(re.findall('EW\d{2}',f)[0][2:])

    if EWXX >=40: 
        return int('{:d}{:02d}'.format(yearSeasonStarted,EWXX))
    return int('{:d}{:02d}'.format(yearSeasonStarted+1,EWXX))

def condenseLocationInfo(d):
    for region in np.arange(1,10+1):
        d.loc[d.location=='HHS Region {:d}'.format(region),'location'] = 'hhs{:d}'.format(region)
    d.loc[d.location=='US National','location'] = 'nat'
    return d

def timeStamp():
    import datetime
    return datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

if __name__ == "__main__":
    FLUSIGHTDIR = '../FluSight-forecasts/2019-2020'
    
    allForecasts = pd.DataFrame()
    for model in os.listdir(FLUSIGHTDIR):
        sys.stdout.write('\x1b[2K\r{:s}'.format(model))
        sys.stdout.flush()
        forecasts = pd.DataFrame()
        for forecastFile in glob('{:s}/{:s}/*'.format(FLUSIGHTDIR,model)):
            forecast = pd.read_csv(forecastFile)
            forecast['EW'] = grabEW(forecastFile,2019) 

            forecasts = forecasts.append(forecast)
           
        forecasts['model'] = model
        allForecasts = allForecasts.append(forecasts)

    allForecasts = condenseLocationInfo(allForecasts)
        
    allForecasts.to_csv('./historicalForecasts/fluSightForecasts_{:s}.csv'.format(timeStamp()),index=False)
    allForecasts.to_csv('./forecasts/fluSightForecasts.csv',index=False)
