import os

# get all dirs
dirs = os.listdir('.')

# get the directories containing RF and LM
winners = [dir for dir in dirs if ('LM' in dir)|('RF' in dir)]

with open('simsList.csv', 'w') as simsList:
    simsList.write('sims\n')
    for dir in winners:
        simsList.write(dir + '\n')