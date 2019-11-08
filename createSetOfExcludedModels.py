#mcandrew

import sys
import numpy as np
import pandas as pd

def timeStamp():
    import datetime
    return datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

if __name__ == "__main__":

    models = pd.read_csv('./forecasts/fluSightForecasts.csv')['model'].unique()

    excluded = { 'FluSightNetwork','UnwghtAvg','Hist-Avg','KISTI(CSB)_26weeks','KoT-adaptive'}
    exclusionList = [ 1 if model in excluded else 0 for model in models  ]

    excludedDataFrame = pd.DataFrame( {'model':models,'excluded':exclusionList} )
    
    excludedDataFrame.to_csv('./historicalExcludedModels/excludedModels_{:s}.csv'.format(timeStamp()),index=False)
    excludedDataFrame.to_csv('./excludedModels/excludedModels.csv',index=False)
