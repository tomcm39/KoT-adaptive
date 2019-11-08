#mcandrew

import sys
import pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

if __name__ == "__main__":

    ensembleForecast = pd.read_csv('./ensembleForecasts/EW43-KoT-adaptive-2019-11-6.csv')
    ensembleForecast = ensembleForecast[ensembleForecast.Type=='Bin']
    
    sumProbs = ensembleForecast.groupby(['Location','Target']).apply( lambda x: pd.Series({'probSum':sum(x.Value)}) )
    
