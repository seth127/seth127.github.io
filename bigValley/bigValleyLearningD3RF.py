# python bigValleyLearningD3RF.py 500 50 new plot

import sys
import os
import time

os.chdir(sys.path[0])

sys.path.append('./bvSimFiles/') # Add location of local packages to path
#sys.path.append('/Users/Seth/Documents/bigValley-Python/bvSimFiles/') # Add location of local packages to path

from bvSimLearning import *

import string
import random

from sklearn.ensemble import RandomForestRegressor

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

## SET PARAMETERS

#max number of years for each epoch
years = int(sys.argv[1]) # default is 500

# number of simulations to run in total before the the program quits
reps = int(sys.argv[2]) # default is 5
### NOTE: IF STARTING ANEW, it will run 500 dumb reps 
#### and THEN start the prescribed number of learning reps

seedReps = 25
bigRun = False # whether to run one for 10,000 years at the end

# either give it 'new' to start over or the ID code of a past trial to continue
if sys.argv[3] == 'new':
  simID = id_generator(3)
  print('STARTING ANEW ')
else:
  simID = sys.argv[3]

# either give it 'plot' to save plotData or anything else to only save epochStats
if sys.argv[4] == 'plot':
  plotting = True
  print('PLOTTING!!!')
else:
  plotting = False
  print('NOT plotting!!!')


#
# make directory for storing
saveDir = 'plotData/RF-' + simID
if not os.path.exists(saveDir):
    os.makedirs(saveDir)

# write file headers for the new file
epochStats = open(saveDir + '/epochStats.csv', "w")
epochStats.write('years,firstExt,firstExtSTD,deadWorld,deadWorldSTD,id,wolfEn,wolfRe,wolfFa,rabbitEn,rabbitRe,rabbitFa,wolfNum,rabbitNum,grassNum,debrisNum\n')
epochStats.close()

#wolf stats
we = 300
wr = 400
wf = 20

#rabbit stats
re = 70
rr = 100
rf = 10

#numbers of each critter
wn = 3
rn = 16
gn = 25
dn = 10

######## PARAMETERS FOR LOADING DATA AND MODELING
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

#################
## RUN THE SIM ##
#################

########
# IF STARTING ANEW, run 500 dumb reps before fitting the initial model
########
if sys.argv[3] == 'new':
    for i in range(0, seedReps):
        # set parameters for this run
        wolfEn = int(we + (np.random.randn(1)[0] * 10))
        wolfRe = int(wr + (np.random.randn(1)[0] * 15))
        if wolfRe < wolfEn * 1.1:
          wolfRe = wolfEn * 1.1
        wolfFa = max(int(wf + (np.random.randn(1)[0] * 5)), 5) # minimum of 5

        rabbitEn = int(re + (np.random.randn(1)[0] * 10))
        rabbitRe = int(rr + (np.random.randn(1)[0] * 10))
        if rabbitRe < rabbitEn * 1.1:
          rabbitRe = rabbitEn * 1.1
        rabbitFa = max(int(rf + (np.random.randn(1)[0] * 5)), 5) # minimum of 5

        # minumum of 1 for each of these
        wolfNum = max(int(wn + (np.random.randn(1)[0] * 3)), 1)
        rabbitNum = max(int(rn + (np.random.randn(1)[0] * 5)), 1)
        grassNum = max(int(gn + (np.random.randn(1)[0] * 10)), 1)
        debrisNum = max(int(dn + (np.random.randn(1)[0] * 10)), 1)

        # RUN THE SIM
        runSim(saveDir,
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
              savePlotDF = plotting,
              saveParamStats = False,
              epochNum = i)
# if not new, assign starting params as where we left off
else:
    previousDF = pd.read_csv(saveDir + '/epochStats.csv')
    startingParams = previousDF.iloc[-1][xList].tolist()
    we = newStartingParams[0]
    wr = newStartingParams[1]
    wf = newStartingParams[2]
    re = newStartingParams[3]
    rr = newStartingParams[4]
    rf = newStartingParams[5]
    wn = newStartingParams[6]
    rn = newStartingParams[7]
    gn = newStartingParams[8]
    dn = newStartingParams[9]

#########
# IF CONTINUING A PREVIOUS RUN, or once the intitial 500 have run,
# RUN THE LEARNING SIM
#########
for i in range(0, reps):
    # re-learn the starting parameters
    newStartingParams = learnParamsRF(100, 
        years, # get 100 options each time
        saveDir,
        we,
        wr,
        wf,
        re,
        rr,
        rf,
        wn,
        rn,
        gn,
        dn,
        xList,
        yList)

    # if we've reached successful stasis (10 in a row that hit 500)
    if isinstance(newStartingParams, (list)):
        print('$$$$$$$$$\n$$$$$$$$$\nSUCCESSFUL STASIS!!!')
        print('ran for ' + str(newStartingParams[1]) + ' years\n$$$$$$$$$\n$$$$$$$$$')
        break

    # FINISH RE-LEARNING, print note
    print('%%%%%%%%\n%%%%%%%%\nRESET STARTING PARAMETERS')
    print(newStartingParams)
    print('%%%%%%%%\n%%%%%%%%\n')
    #print('continuing in ...')
    #print('5'); time.sleep(1); print('4'); time.sleep(1); print('3'); time.sleep(1); print('2'); time.sleep(1); print('1'); time.sleep(1)

    
    # reset parameters
    we = int(newStartingParams['wolfEn'])
    wr = int(newStartingParams['wolfRe'])
    wf = int(newStartingParams['wolfFa'])
    re = int(newStartingParams['rabbitEn'])
    rr = int(newStartingParams['rabbitRe'])
    rf = int(newStartingParams['rabbitFa'])
    wn = int(newStartingParams['wolfNum'])
    rn = int(newStartingParams['rabbitNum'])
    gn = int(newStartingParams['grassNum'])
    dn = int(newStartingParams['debrisNum'])
    '''
    # set parameters for this run
    wolfEn = int(we + (np.random.randn(1)[0] * 10))
    wolfRe = int(wr + (np.random.randn(1)[0] * 15))
    if wolfRe < wolfEn * 1.1:
      wolfRe = wolfEn * 1.1
    wolfFa = max(int(wf + (np.random.randn(1)[0] * 5)), 5) # minimum of 5

    rabbitEn = int(re + (np.random.randn(1)[0] * 10))
    rabbitRe = int(rr + (np.random.randn(1)[0] * 10))
    if rabbitRe < rabbitEn * 1.1:
      rabbitRe = rabbitEn * 1.1
    rabbitFa = max(int(rf + (np.random.randn(1)[0] * 5)), 5) # minimum of 5

    # minumum of 1 for each of these
    wolfNum = max(int(wn + (np.random.randn(1)[0] * 3)), 1)
    rabbitNum = max(int(rn + (np.random.randn(1)[0] * 5)), 1)
    grassNum = max(int(gn + (np.random.randn(1)[0] * 10)), 1)
    debrisNum = max(int(dn + (np.random.randn(1)[0] * 10)), 1)
    '''

    # RUN THIS ITERATION
    runSim(saveDir,
          years,
          we,
          wr,
          wf,
          re,
          rr,
          rf,
          wn,
          rn,
          gn,
          dn,
          endOnOverflow = True,
          savePlotDF = plotting,
          saveParamStats = False,
          epochNum = (i + seedReps))

if bigRun == True:
    # ONCE WE REACHED SUCCESS, RUN A BIG ONE
    runSim(saveDir,
          10000,
          we,
          wr,
          wf,
          re,
          rr,
          rf,
          wn,
          rn,
          gn,
          dn,
          endOnOverflow = False,
          savePlotDF = plotting,
          saveParamStats = False,
          epochNum = (i + seedReps + 1))
