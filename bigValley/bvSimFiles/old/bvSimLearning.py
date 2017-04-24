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


######## PARAMETERS FOR LOADING DATA AND MODELING
'''
simCols = ['tests','years','firstExt', 'firstExtSTD', 'deadWorld', 'deadWorldSTD', 'id',
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
          file_name,
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
    simDF = pd.read_csv(file_name)
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


def learnParamsLM(file_name, years,
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
    simDF = pd.read_csv(file_name)
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

def testLife(tests, 
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
        saveYearStats = False,
        savePlotDF = False,
        epochNum = 1):
    testStats = []
    for i in range(0, tests):
        #create an instance of World 
        bigValley = World(5)
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
            saveYearStats = saveYearStats,
            savePlotDF = savePlotDF,
            epochNum = epochNum)
        testStats.append(test)
        print('testStats ' + str(i) + ' ::: ' + str(testStats))
        
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

def runSim(file_name,
          tests,
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
          saveYearStats=False,
          savePlotDF = False,
          epochNum = 1):
    start=datetime.datetime.now()
    #file_name = 'data/' + str(tests) + 'x' + str(years) + '-' + id_generator() + '.csv' 
    testDF = testLife(tests, 
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
        saveYearStats = saveYearStats,
        savePlotDF = savePlotDF,
        epochNum = epochNum)
    thisSim = [
        tests,
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
    file = open(file_name, "a")
    #write the new line
    file.write(str(thisSim).strip('[]') + '\n')
    #print the number of lines logged to the file
    #file_len(file_name)
    print("%d lines in your choosen file" % len(open(file_name).readlines()))
    ##print "%d lines in your choosen file" % len(file.readlines())

    #close the file
    file.close()
    print(datetime.datetime.now()-start)
    print('%%%%%%%%')


def runSimLearningRF1(file_name, 
          tests,
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
          saveYearStats=False,
          savePlotDF = False,
          epochNum = 1):
    start=datetime.datetime.now()
    #file_name = 'data/' + str(tests) + 'x' + str(years) + '-' + id_generator() + '.csv' 
    
    ####### DO THE LEARNING

    winner = learnParamsRF(optsNum,
          file_name,
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

    testDF = testLife(tests, 
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
        saveYearStats = saveYearStats,
        savePlotDF = savePlotDF,
        epochNum = epochNum)
    thisSim = [
        tests,
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
    file = open(file_name, "a")
    #write the new line
    file.write(str(thisSim).strip('[]') + '\n')
    #print the number of lines logged to the file
    #file_len(file_name)
    print("%d lines in your choosen file" % len(open(file_name).readlines()))
    ##print "%d lines in your choosen file" % len(file.readlines())

    #close the file
    file.close()
    print(datetime.datetime.now()-start)
    print('%%%%%%%%')
    return 'finished thisSim'


