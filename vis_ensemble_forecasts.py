#mcandrew

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

import datetime
from epiweeks import Week, Year

def fromDateTime2EW(dt):
    w = Week.fromdate(dt.year,dt.month,dt.day)
    return "{:4}{:2}".format(w.year,w.week)

def computeTargetILIepiWeek(row):
    forecastWeek = row.surveillanceWeek
    weekAhead = int(row.Target.replace(' wk ahead',''))
    iliYear,iliWeek = int(str(forecastWeek)[:3+1]),int(str(forecastWeek)[4:])
    iliEW = Week(iliYear,iliWeek) + int(weekAhead)
    iliEW = int("{:04d}{:02d}".format(iliEW.year,iliEW.week))
    row['targetWeek'] = iliEW
    return row

def reformat_region(row):
    import re
    if 'hhs' in row.region:
        regionNum = int(re.findall('\d+',row.region)[-1])
        row['Location'] = "HHS Region {:d}".format(regionNum)
    else:
        row['Location'] = "US National"
    return row

def mm2inch(x):
    return x/25.4


if __name__ == "__main__":

    ensembleForecasts = pd.read_csv('./ensembleForecastsForAllEW/EW43-KoT-adaptive-2019-11-5.csv')
    
    iliData = pd.read_csv('./data/epiData.csv')
    iliData = iliData.apply( reformat_region,1 )

    ensembleForecasts = ensembleForecasts.rename(columns={'EW':'surveillanceWeek'})
    ensembleForecasts  = ensembleForecasts.loc[ensembleForecasts.Type=='Bin',:]

    ensembleForecastsPoint = ensembleForecasts.loc[ensembleForecasts.Target.str.contains('wk ahead'),:]
    ensembleForecastsPoint = ensembleForecastsPoint.apply(computeTargetILIepiWeek,1)
    
    ensembleAndTruth = ensembleForecastsPoint.merge(iliData,left_on = ['targetWeek','Location'], right_on = ['EW','Location']) 


    for EW in list(ensembleAndTruth.surveillanceWeek.unique()):
        i,j=0,0
        fig,axs = plt.subplots(4,11)
        for target in np.arange(1,4+1):
            j=0
            for region in np.arange(1,11+1):
                ax = axs[i,j]

                trgt = "{:d} wk ahead".format(target)
                location = "HHS Region {:d}".format(region) if region <11 else "US National"

                subset = ensembleAndTruth.loc[ensembleAndTruth.surveillanceWeek==EW,:]
                subset = subset.loc[ (ensembleAndTruth.Target==trgt) & (ensembleAndTruth.Location==location),:]
                subset['x'] = subset.Bin_start_incl.astype(float)
                subset = subset.sort_values('x')

                ax.plot(subset.x,subset.Value,'k-')

                ax.set_xticks([0,1,2,3,4,5,6,7,8,9,10,11,12,13])
                ax.set_yticks([])

                ax.tick_params(direction='in',size=1.)

                ax.set_xticklabels(ax.get_xticks(),fontsize=2)
                ax.set_yticklabels(ax.get_yticks(),fontsize=2)

                if i==0:
                    ax.set_title(location.replace(' Region ',''),fontsize=10)
                if j==0:
                    ax.set_ylabel(trgt,fontsize=10)

                try:
                    ax.plot( [subset.wili.iloc[0]]*2,[0,max(subset.Value)],'r--')
                except:
                    pass
                j+=1
            i+=1

        fig.set_size_inches(mm2inch(183),mm2inch(183)/1.5)
        plt.savefig('./vis/vis_forecastCheck_survWeek_{:d}.pdf'.format(EW))
        plt.close()
