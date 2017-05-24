import datetime
import sys
import pandas as pd
import numpy as np


from bvWorldEvo import *
from bvLifeEvo import *

import string
import random

from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))
#'file' + id_generator()

def makeLongEpochStats(df, saveDir, scaleFactor=10, learningCutoff=0):
    # define the stats to summarize
    stats = ['deadWorld','wolfEn', 'wolfRe', 'wolfFa', 'rabbitEn', 'rabbitRe', 'rabbitFa', 
           'wolfNum', 'rabbitNum', 'grassNum', 'debrisNum']
    # trim the data to the observations we want to use
    dfLen = df.shape[0]
    df = df.iloc[learningCutoff:dfLen]
    # create label vector
    labels = []
    for num in range(1, scaleFactor+1):
        labels += [num for x in range(int(np.ceil(dfLen/scaleFactor)))]
    # assign label vector to column
    df['labels'] = labels[:dfLen]
    # convert to long format
    df_long = pd.melt(df, id_vars=['labels'], value_vars=stats)
    # summarize each stat by label
    df_mean = df_long.groupby(['labels','variable'])['value'].mean()
    # write to csv
    pd.DataFrame(df_mean).to_csv(saveDir + '/epochStats-long.csv')

######## PARAMETERS FOR LOADING DATA AND MODELING
'''
simCols = ['years','firstExt', 'firstExtSTD', 'deadWorld', 'deadWorldSTD', 'id',
      'wolfEn',
      'wolfRe',
      'wolfFa',
      'rabbitEn',
      'rabbitRe',
      'rabbitFa',
      'wolfNum',
      'rabbitNum',
      'grassNum',
      'debrisNum']
'''
yList = ['firstExt']
xList = ['wolfEn',
          'wolfRe',
          'wolfFa',
          'rabbitEn',
          'rabbitRe',
          'rabbitFa',
          'wolfNum',
          'rabbitNum',
          'grassNum',
          'debrisNum']

def learnParamsRF(optsNum, years,
          saveDir,
          wolfEn,
          wolfRe,
          wolfFa,
          rabbitEn,
          rabbitRe,
          rabbitFa,
          wolfNum,
          rabbitNum,
          grassNum,
          debrisNum,
          xList,
          yList):
    # get the latest sim data
    simDF = pd.read_csv(saveDir + '/epochStats.csv')
    # check if we've reached successful stasis (10 in a row that hit the max years)
    if min(simDF.iloc[-10:]['deadWorld']) == years:
        return ['END', simDF.shape[0]]

    # train the model
    rfModel=RandomForestRegressor(n_estimators=300,
                            max_depth=None, 
                            max_features=.8,
                            min_samples_split=1,
                            #random_state=0,
                            n_jobs=-1)

    rfModel.fit(simDF[xList], np.array(simDF[yList]).ravel())

    # get options
    xs = []
    for i in range(0,optsNum):
        we = max(int(wolfEn + (np.random.randn(1)[0] * 10)), 100) # minimum of 100
        wr = int(wolfRe + (np.random.randn(1)[0] * 15))
        if wr < we * 1.1:
            wr = we * 1.1
        wf = max(int(wolfFa + (np.random.randn(1)[0] * 5)), 5) # minimum of 5

        re = max(int(rabbitEn + (np.random.randn(1)[0] * 10)), 25) # minimum of 25
        rr = int(rabbitRe + (np.random.randn(1)[0] * 10))
        if rr < re * 1.1:
            rr = re * 1.1
        rf = max(int(rabbitFa + (np.random.randn(1)[0] * 5)), 5) # minimum of 5

        # minumum of 1 for each of these
        wn = max(int(wolfNum + (np.random.randn(1)[0] * 3)), 1)
        rn = max(int(rabbitNum + (np.random.randn(1)[0] * 5)), 1)
        gn = max(int(grassNum + (np.random.randn(1)[0] * 10)), 1)
        dn = max(int(debrisNum + (np.random.randn(1)[0] * 10)), 1)
        xs.append([we, wr, wf, re, rr, rf, wn, rn, gn, dn])

    optsDF = pd.DataFrame(xs, columns = xList)

    # predict the best of the options
    optsDF['preds'] = rfModel.predict(optsDF)
    winner = optsDF[optsDF.preds == max(optsDF.preds)]

    # returns the parameter values for the best option (as well as the predicted firstExt)
    return winner


def learnParamsLM(saveDir, 
          years,
          wolfEn,
          wolfRe,
          wolfFa,
          rabbitEn,
          rabbitRe,
          rabbitFa,
          wolfNum,
          rabbitNum,
          grassNum,
          debrisNum,
          xList,
          yList, incremental = True):
    # get the latest sim data
    simDF = pd.read_csv(saveDir + '/epochStats.csv')
    # check if we've reached successful stasis (10 in a row that hit max years)
    if min(simDF.iloc[-10:]['deadWorld']) == years:
        return ['END', simDF.shape[0]]

    # train the model
    lm = LinearRegression().fit(simDF[xList], np.array(simDF[yList]).ravel())

    # round coefficients to 1 or -1, or the nearest integer if |coef| > 1
    def pushToInt(num):
        if 0 < num <= 1:
            return int(1)
        elif 0 > num >= -1:
            return int(-1)
        else:
            return int(round(num, 0))

    def returnSign(num):
        if 0 < num:
            return int(1)
        elif 0 > num :
            return int(-1)
        else:
            return 0

    if incremental == True:
        # push to nearest int, multiply first six by 5
        adjustments = [returnSign(x)*5 for x in lm.coef_[0:6]] + [returnSign(x) for x in lm.coef_[6:]]
    else:
        # for first six, multiply by 10
        # for critter numbers just push to nearest int
        adjustments = [int(x*10) for x in lm.coef_[0:6]] + [pushToInt(x) for x in lm.coef_[6:]]

    # add this list to previous parameters to adjust each iteration
    return adjustments

def testLife(saveDir,
        years, 
        wolfEn,
        wolfRe,
        wolfFa,
        rabbitEn,
        rabbitRe,
        rabbitFa,
        wolfNum,
        rabbitNum,
        grassNum,
        debrisNum,
        endOnExtinction = True,
        endOnOverflow = True,
        saveParamStats = False,
        savePlotDF = False,
        epochNum = 1):
    testStats = []

    #create an instance of World 
    bigValley = World(5,saveDir)
    print(datetime.datetime.now())

    #define your life forms
    newLife(Predator('wolf', energy = wolfEn, repro = wolfRe, fatigue = wolfFa), 
            bigValley, 'wolf') # adding in the parameters from above
    newLife(Prey('rabbit', energy = rabbitEn, repro = rabbitRe, fatigue = rabbitFa), 
            bigValley, 'rabbit') # adding in the parameters from above
    newLife(Plant('grass'), bigValley, 'grass')
    newLife(Rock('debris'), bigValley, 'debris')

    #now populate the world
    populate(bigValley, 'wolf', wolfNum)
    populate(bigValley, 'rabbit', rabbitNum)
    populate(bigValley, 'grass', grassNum)
    populate(bigValley, 'debris', debrisNum)
    
    #now run the test
    test = bigValley.silentTime(years, 
        yearlyPrinting = True, 
        endOnExtinction = endOnExtinction, 
        endOnOverflow = endOnOverflow,
        saveParamStats = saveParamStats,
        savePlotDF = savePlotDF,
        epochNum = epochNum)
    testStats.append(test)
    print('testStats ::: ' + str(testStats))
    
    # return stats for each test
    testDF = pd.DataFrame(testStats, columns=['firstExt', 'deadWorld', 'id'])

    #return testStats
    print(testDF)
    return testDF



# function to count the lines in a file (for seeing how many epochs have been logged)
'''
def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    	#return i + 1
    	print(str(fname) + ' is now ' + str(i + 1) + ' lines long.')
'''

def runSim(saveDir,
          years,
          wolfEn,
          wolfRe,
          wolfFa,
          rabbitEn,
          rabbitRe,
          rabbitFa,
          wolfNum,
          rabbitNum,
          grassNum,
          debrisNum,
          endOnExtinction=True,
          endOnOverflow=True,
          saveParamStats=False,
          savePlotDF = False,
          epochNum = 1):
    start=datetime.datetime.now()
    #file_name = 'data/' + str(tests) + 'x' + str(years) + '-' + id_generator() + '.csv' 
    testDF = testLife(saveDir, 
        years, 
        wolfEn,
        wolfRe,
        wolfFa,
        rabbitEn,
        rabbitRe,
        rabbitFa,
        wolfNum,
        rabbitNum,
        grassNum,
        debrisNum,
        endOnExtinction = endOnExtinction,
        endOnOverflow = endOnOverflow,
        saveParamStats = saveParamStats,
        savePlotDF = savePlotDF,
        epochNum = epochNum)
    thisSim = [
        years,
        round(np.mean(testDF['firstExt']), 2), # first extinction
        round(np.std(testDF['firstExt']), 2),
        round(np.mean(testDF['deadWorld']), 2), # dead world
        round(np.std(testDF['deadWorld']), 2),
        ','.join(testDF['id'].tolist()),
        wolfEn,
        wolfRe,
        wolfFa,
        rabbitEn,
        rabbitRe,
        rabbitFa,
        wolfNum,
        rabbitNum,
        grassNum,
        debrisNum]
    print(thisSim)
    #open the file
    file = open(saveDir + '/epochStats.csv', "a")
    #write the new line
    file.write(str(thisSim).strip('[]') + '\n')
    #close the file
    file.close()

    #print the number of lines logged to the file
    #epochsRun = len(open(saveDir + '/epochStats.csv').readlines())
    epochStats = pd.read_csv(saveDir + '/epochStats.csv')
    epochsRun = epochStats.shape[0]
    print("%d EPOCHS HAVE BEEN RUN SO FAR" % epochsRun)
    
    # if more than 20, calculate long stats
    if epochsRun > 20:
        makeLongEpochStats(epochStats, saveDir)
    
    print(datetime.datetime.now()-start)
    print('%%%%%%%%')

##############
def continentLife(saveDir,
        years, 
        idList,
        endOnExtinction = True,
        endOnOverflow = True,
        saveParamStats = False,
        savePlotDF = False,
        epochNum = 1):
    testStats = []

    #create an instance of World 
    bigValley = World(5, saveDir)
    print(datetime.datetime.now())

    #### load continent stats
    contDF = pd.read_csv('testData/continentStats.csv', index_col=0)

    if idList == 'random': #######haven't tested this #######################
        idList = np.random.choice(contDF.index, 3) ### pick three ###########

    ##### CURRENTLY ONLY WORKS FOR 3 #####
    offsets = [[-25,-25], [25,-25], [0,17]]

    # call the stats for each id and feed them in
    for i, runId in enumerate(idList): 
        #define your life forms
        '''
        newLife(Predator('wolf', energy = contDF.loc[runId,'wolfEn'], repro = contDF.loc[runId,'wolfRe'], fatigue = contDF.loc[runId,'wolfFa']), 
                bigValley, 'wolf') # adding in the parameters from above
        newLife(Prey('rabbit', energy = contDF.loc[runId,'rabbitEn'], repro = contDF.loc[runId,'rabbitRe'], fatigue = contDF.loc[runId,'rabbitFa']), 
                bigValley, 'rabbit') # adding in the parameters from above
        newLife(Plant('grass'), bigValley, 'grass')
        newLife(Rock('debris'), bigValley, 'debris')

        #now populate the world
        populate(bigValley, 'wolf', contDF.loc[runId,'wolfNum'], offset = offsets[i]) 
        populate(bigValley, 'rabbit', contDF.loc[runId,'rabbitNum'], offset = offsets[i])
        populate(bigValley, 'grass', contDF.loc[runId,'grassNum'], offset = offsets[i])
        populate(bigValley, 'debris', contDF.loc[runId,'debrisNum'], offset = offsets[i])
        '''
        newLife(Predator(runId + 'wolf', energy = contDF.loc[runId,'wolfEn'], repro = contDF.loc[runId,'wolfRe'], fatigue = contDF.loc[runId,'wolfFa']), 
                bigValley, runId + 'wolf') # adding in the parameters from above
        newLife(Prey(runId + 'rabbit', energy = contDF.loc[runId,'rabbitEn'], repro = contDF.loc[runId,'rabbitRe'], fatigue = contDF.loc[runId,'rabbitFa']), 
                bigValley, runId + 'rabbit') # adding in the parameters from above
        newLife(Plant('grass'), bigValley, 'grass')
        newLife(Rock('debris'), bigValley, 'debris')

        #now populate the world
        populate(bigValley, runId + 'wolf', contDF.loc[runId,'wolfNum'], offset = offsets[i]) 
        populate(bigValley, runId + 'rabbit', contDF.loc[runId,'rabbitNum'], offset = offsets[i])
        populate(bigValley, 'grass', contDF.loc[runId,'grassNum'], offset = offsets[i])
        populate(bigValley, 'debris', contDF.loc[runId,'debrisNum'], offset = offsets[i])
        print('offset' + str(i) + str(offsets[i]))
    #now run the test
    test = bigValley.silentTime(years, 
        yearlyPrinting = True, 
        endOnExtinction = endOnExtinction, 
        endOnOverflow = endOnOverflow,
        saveParamStats = saveParamStats,
        savePlotDF = savePlotDF,
        continents = True,
        epochNum = epochNum)
    testStats.append(test)
    print('testStats ::: ' + str(testStats))
    
    # return stats for each test
    testDF = pd.DataFrame(testStats, columns=['firstExt', 'deadWorld', 'id'])

    #return testStats
    print(testDF)
    return testDF



##############

def runSimLearningRF1(saveDir, 
          years,
          wolfEn,
          wolfRe,
          wolfFa,
          rabbitEn,
          rabbitRe,
          rabbitFa,
          wolfNum,
          rabbitNum,
          grassNum,
          debrisNum,
          optsNum=25,
          endOnExtinction=True,
          endOnOverflow=True,
          saveParamStats=False,
          savePlotDF = False,
          epochNum = 1):
    start=datetime.datetime.now()

    ####### DO THE LEARNING

    winner = learnParamsRF(optsNum,
          saveDir,
          wolfEn,
          wolfRe,
          wolfFa,
          rabbitEn,
          rabbitRe,
          rabbitFa,
          wolfNum,
          rabbitNum,
          grassNum,
          debrisNum,
          xList,
          yList)

    # if we've reached successful stasis (10 in a row that hit max years)
    if isinstance(winner, (list)):
        return winner

    ####### RUN THE SIM

    testDF = testLife(saveDir,
        years, 
        int(winner['wolfEn']),
        int(winner['wolfRe']),
        int(winner['wolfFa']),
        int(winner['rabbitEn']),
        int(winner['rabbitRe']),
        int(winner['rabbitFa']),
        int(winner['wolfNum']),
        int(winner['rabbitNum']),
        int(winner['grassNum']),
        int(winner['debrisNum']),
        endOnExtinction = endOnExtinction,
        endOnOverflow = endOnOverflow,
        saveParamStats = saveParamStats,
        savePlotDF = savePlotDF,
        epochNum = epochNum)
    thisSim = [
        years,
        round(np.mean(testDF['firstExt']), 2), # first extinction
        round(np.std(testDF['firstExt']), 2),
        round(np.mean(testDF['deadWorld']), 2), # dead world
        round(np.std(testDF['deadWorld']), 2),
        ','.join(testDF['id'].tolist()),
        int(winner['wolfEn']),
        int(winner['wolfRe']),
        int(winner['wolfFa']),
        int(winner['rabbitEn']),
        int(winner['rabbitRe']),
        int(winner['rabbitFa']),
        int(winner['wolfNum']),
        int(winner['rabbitNum']),
        int(winner['grassNum']),
        int(winner['debrisNum']), int(winner['preds'])]
    print(thisSim)
    print('$$$$$\n PREDICTED FirstExt: ' + str(int(winner['preds'])) + '\n$$$$$')
    #open the file
    file = open(saveDir + '/epochStats.csv', "a")
    #write the new line
    file.write(str(thisSim).strip('[]') + '\n')
    #print the number of lines logged to the file
    #file_len(file_name)
    print("%d lines in your choosen file" % len(open(saveDir + '/epochStats.csv').readlines()))
    ##print "%d lines in your choosen file" % len(file.readlines())

    #close the file
    file.close()
    print(datetime.datetime.now()-start)
    print('%%%%%%%%')
    return 'finished thisSim'


