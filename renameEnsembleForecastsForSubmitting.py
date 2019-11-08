#mcandrew

import numpy as np
import pandas as pd
from glob import glob
import re

if __name__ == "__main__":

    for forecast in glob('./ensembleForecasts/*'):
        EW,date = re.findall('(EW.*)-KoT-adaptive-(.*).csv',forecast)[0]
        year = date.split('-')[0]
        
        d = pd.read_csv(forecast)
        d.to_csv('./submittedForecasts/{:s}-{:s}-KoT-adaptive.csv'.format(EW,year),index=False)
