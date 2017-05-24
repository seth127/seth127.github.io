# python bigValleyLearningD3LM.py 500 50 new plot

import sys
import os
import time

os.chdir(sys.path[0])

sys.path.append('./bvSimFiles/') # Add location of local packages to path
#sys.path.append('/Users/Seth/Documents/bigValley-Python/bvSimFiles/') # Add location of local packages to path

from bvSimLearning import *
#from bvSimArchiver import *

import string
import random

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

# make directory for storing
saveDir = 'plotData/LM-' + simID
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
    # set starting params for learning
    newStartingParams = [we,wr,wf,re,rr,rf,wn,rn,gn,dn,]
else:
    previousDF = pd.read_csv(saveDir + '/epochStats.csv')
    newStartingParams = previousDF.iloc[-1][xList].tolist()

#########
# IF CONTINUING A PREVIOUS RUN, or once the intitial 500 have run,
# RUN THE LEARNING SIM
#########

for i in range(0, reps):
    # set previous starting params from the newStartingParams from the last run
    previousParams = newStartingParams
    # re-learn the starting parameters
    adjustments = learnParamsLM(saveDir, 
        years,
        previousParams[0],
        previousParams[1],
        previousParams[2],
        previousParams[3],
        previousParams[4],
        previousParams[5],
        previousParams[6],
        previousParams[7],
        previousParams[8],
        previousParams[9],
        xList,
        yList,
        incremental = True) ### THIS IS THE MAIN DIFFERENCE BETWEEN LM1 AND LM2

    # if we've reached successful stasis (10 in a row that hit 500)
    if adjustments[0] == 'END':
        print('$$$$$$$$$\n$$$$$$$$$\nSUCCESSFUL STASIS!!!')
        print('ran for ' + str(adjustments[1]) + ' years\n$$$$$$$$$\n$$$$$$$$$')
        break

    # adjust previousParams and set as newStartingParams
    newStartingParams = np.array(previousParams) + np.array(adjustments)

    # FINISH RE-LEARNING, print note
    print('%%%%%%%%\n%%%%%%%%\nRESET STARTING PARAMETERS.\nAdjustments:')
    print(adjustments)
    #print(newStartingParams)
    print('%%%%%%%%\n%%%%%%%%\n')
    #print('continuing in ...')
    #print('5'); time.sleep(1); print('4'); time.sleep(1); print('3'); time.sleep(1); print('2'); time.sleep(1); print('1'); time.sleep(1)

    # set parameters for this run
    wolfEn = max(newStartingParams[0], 100) # minimum of 100
    wolfRe = max(newStartingParams[1], round((wolfEn * 1.1), 0)) # minimum of wolfEn * 1.1
    wolfFa = max(newStartingParams[2], 5) # minimum of 5

    rabbitEn = max(newStartingParams[3], 25) # minimum of 25
    rabbitRe = max(newStartingParams[4], round((rabbitEn * 1.1), 0)) # minimum of rabbitEn * 1.1
    rabbitFa = max(newStartingParams[5], 5) # minimum of 5

    # minumum of 1 for each of these
    wolfNum = int(max(newStartingParams[6], 1))
    rabbitNum = int(max(newStartingParams[7], 1))
    grassNum = int(max(newStartingParams[8], 1))
    debrisNum = int(max(newStartingParams[9], 1))


    # RUN THIS ITERATION
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
          endOnOverflow = True,
          savePlotDF = plotting,
          saveParamStats = False,
          epochNum = (i + seedReps))
    print(adjustments)


if bigRun == True:
    # ONCE WE REACHED SUCCESS, RUN A BIG ONE
    # set parameters for this run
    wolfEn = max(newStartingParams[0], 100) # minimum of 100
    wolfRe = max(newStartingParams[1], round((wolfEn * 1.1), 0)) # minimum of wolfEn * 1.1
    wolfFa = max(newStartingParams[2], 5) # minimum of 5

    rabbitEn = max(newStartingParams[3], 25) # minimum of 25
    rabbitRe = max(newStartingParams[4], round((rabbitEn * 1.1), 0)) # minimum of rabbitEn * 1.1
    rabbitFa = max(newStartingParams[5], 5) # minimum of 5

    # minumum of 1 for each of these
    wolfNum = max(int(max(newStartingParams[6], 1)), 1)
    rabbitNum = max(int(max(newStartingParams[7], 1)), 1)
    grassNum = int(max(newStartingParams[8], 1))
    debrisNum = int(max(newStartingParams[9], 1))

    runSim(saveDir,
          10000,
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
          endOnOverflow = False,
          saveParamStats = True,
          savePlotDF = plotting,
          epochNum = (i + seedReps + 1))
