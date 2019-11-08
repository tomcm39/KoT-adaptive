#mcandrew

import pandas as pd

if __name__ == "__main__":

    scores = pd.read_csv('./scores/logScores.csv')
    numModels = len(scores.model.unique())

    fout = open("./checks/numModelsWithScores.csv",'w')
    fout.write("Number of Models with logscores = {:d}\n".format(numModels))
    for model in sorted(scores.model.unique()):
        fout.write("{:s}\n".format(model))
    fout.close()
    
