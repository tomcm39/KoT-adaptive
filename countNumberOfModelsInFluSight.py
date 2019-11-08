#mcandrew

import pandas as pd

if __name__ == "__main__":

    forecasts = pd.read_csv('./forecasts/fluSightForecasts.csv')
    numModels = len(forecasts.model.unique())

    fout = open("./checks/numModelsInFluSight.csv",'w')
    fout.write("Number of Models in FluSight = {:d}\n".format(numModels))
    for model in sorted(forecasts.model.unique()):
        fout.write("{:s}\n".format(model))
    fout.close()
