#mcandrew

import pandas as pd
import numpy as np

if __name__ == "__main__":

    forecasts = pd.read_csv('./forecasts/fluSightForecasts.csv')
    numberOfForecastsPerModel = forecasts.groupby(["model","EW"]).apply( lambda x: pd.Series({'N':np.shape(x)[0]})).reset_index()
    numberOfForecastsPerModel.to_csv("./checks/numberOfForecastsPerModel.csv")
