# -*- coding: utf-8 -*-
import numpy as np
import random
#from numpy.random import randn
import pandas as pd
#from bokeh.charts import Scatter, output_notebook, show
#output_notebook() ## sets it up for output in the notebook

from collections import Counter

import string
import random

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

import time

#define World class
class World:
    def __init__(self, size):
        print('You have created the world.')
        self.year = 0
        self.size = size
        #self.df = pd.DataFrame([], columns = ['lat', 'long', 'name', 'kingdom', 'energy'])
        self.dict = {}
        self.bookOfLife = {}
        
        self.id = id_generator()
        print(self.id)

        self.yearStats = []
        self.paramStats = []
        self.crakeStats = [1,1, self.id]

    #####################
    # HELPER FUNCTIONS ##
    #####################
    
    # creates an instance of a critter
    def create(self, name, location = 'random'):
        # pick location for new life
        if location == 'random':
            w1 = np.random.randn(1, 2)[0] * self.size
            w1 = w1.tolist()
            #w1 = [round(num, 0) for num in w1]
            w1 = [int(num) for num in w1]
            coords = ",".join([str(x) for x in w1])
            # check if a critter is already there, if so pick a new spot
            while coords in self.dict.keys():
                w1 = np.random.randn(1, 2)[0] * self.size
                w1 = w1.tolist()
                w1 = [int(num) for num in w1]
                coords = ",".join([str(x) for x in w1])
        else:
            coords = location
            
        # check if this critter is in the bookOfLife and if so create it
        if name in self.bookOfLife.keys():
            self.dict[coords] = self.bookOfLife[name].birthStats()
        else:
            print(name + " is not in the Book Of Life.")

    # reproduces an instance of a critter with same starting stats as it's parent
    def reproduce(self, critter, location):  
        # copy parent stats to child from inheritance dictionary (add some slight variation)
        energy = critter[2]['birthEn'] + (np.random.randn(1)[0] * 2)
        repro = critter[2]['birthRe'] + (np.random.randn(1)[0] * 1)
        fatigue = critter[2]['birthFa'] + (np.random.randn(1)[0] * 0.5)
        
        ########
        # set some constraints so that reproduction doesn't get out of control
        ########
        if fatigue < 5:
            fatigue = 5
        if repro < energy * 1.1:
            repro = energy * 1.1

        inheritance = {'birthEn': energy, 'birthRe': repro, 'birthFa': fatigue}
        lifeStats = [energy, repro, fatigue]

        self.dict[location] = critter[0:2] + [inheritance] + lifeStats
          

    # gets parameter stats for each type of critter
    def getParamStats(self):
        paramStats = []
        for name in self.bookOfLife.keys():
            # skip if it's a Rock
            if self.bookOfLife[name].kingdom == 'Rock':
                continue

            # subset the critter type you want
            picks = [x for x in self.dict.values() if x[0] == name]
            # get stats
            count = len(picks)
            if count > 0:
                meanEnergy = round(np.mean([x[3] for x in picks]), 1)
                meanRepro = round(np.mean([x[4] for x in picks]), 1)
                meanFatigue = round(np.mean([x[5] for x in picks]), 1)
            else:
                meanEnergy = None
                meanRepro = None
                meanFatigue = None
            # save stats
            paramStats = paramStats + [count, meanEnergy, meanRepro, meanFatigue]
        #     
        return paramStats

        # gets parameter stats for each type of critter
    def getParamCols(self):
        paramCols = []
        for name in self.bookOfLife.keys():
            # skip if it's a Rock
            if self.bookOfLife[name].kingdom == 'Rock':
                continue

            # save names of Cols
            #paramCols = paramCols + [name+'Count', name+'Energy', name+'Repro', name+'Fatigue']
            paramCols = paramCols + [name+'Num', name+'En', name+'Re', name+'Fa']
        #     
        return paramCols


    #######################################
    # FUNCTION TO ACTUALLY RUN THE WORLD ##
    #######################################

    def silentTime(self, number, 
        endOnExtinction = True, 
        endOnOverflow = True, 
        yearlyPrinting = True, 
        saveYearStats = False,
        savePlotDF = False,
        epochNum = 1):

        # set the number of species in the world
        biomeCount = len(set([critter[0] for critter in self.dict.values() if critter[1] != 'Plant']))
        print(biomeCount)
        # set the boolean for the first extinction
        firstExt = False
        # set the initial values of paramStats
        self.paramCols = self.getParamCols()
        self.paramStats.append(self.getParamStats())
        # initialize plotting Data Frame
        if savePlotDF == True:
            plotCols = ['year', 'lat', 'long', 'name', 'energy']
            plotDF = pd.DataFrame()

        for i in range(0, number):
            self.year += 1
            #print('Year ' + str(self.year))
            # keep track of critters that starve or get eaten
            dead = []
            # loop through each critter and let it act
            critterkeys = [x for x in self.dict.keys()]
            #for key in self.dict.keys():
            for key in critterkeys:
                # get critter stats
                #critter = self.dict[key]
                # load the critter for this key, skip ahead if he's already been eaten
                try: 
                    critter = self.dict[key]
                except:
                    continue

                # get coordinates as integers
                coords = [int(coord) for coord in key.split(',')]
                #print(coords)

                # call up the critter from the bookOfLife
                # then feed its View to its act() method
                action = self.bookOfLife[critter[0]].act(critter, View(self.dict, coords))
                # action will be a dict with the following:
                ## action['location'] = the coordinates in string form
                ## action['act'] = the name of the action
                ## action['energy'] = the change in energy resulting form the action

                if action != None:
                    # reproduce
                    if action['act'] == 'repro':
                        # if rock, make grass. otherwise reproduce
                        if critter[1] == 'Rock':
                            self.create('grass', location = action['location'])
                        else:
                            self.reproduce(critter, location = action['location'])
                        #update with new stats
                        #self.df.loc[index, 'energy'] = int(row['energy']) + int(action['energy'])
                        self.dict[key][3] = self.dict[key][3] + action['energy']
                    # delete anything that it's about to eat
                    elif action['act'] == 'eat':
                        # copy the critter that's about to be eaten
                        chomp = self.dict[action['location']]
                        #
                        ######## print the animal before it has eaten
                        #print(critter[0] + ' eats ' + chomp[0] + ' at ' + action['location'])
                        #
                        # copy critter to new location
                        self.dict[action['location']] = critter
                        # delete critter from old location
                        #dead += [key]
                        del self.dict[key]
                        # add the energy for the eaten animal
                        self.dict[action['location']][3] = self.dict[action['location']][3] + action['energy']
                        #######print the animal after it has eaten
                        #print(self.dict[action['location']])
                    # 
                    elif action['act'] == 'grow':
                        self.dict[key][3] = self.dict[key][3] + action['energy']
                    #
                    #elif action['act'] == 'move':
                    else:
                        #update with new stats
                        # copy critter to new location
                        self.dict[action['location']] = critter
                        # delete critter from old location
                        del self.dict[key]
                        # add the energy for the eaten animal
                        self.dict[action['location']][3] = self.dict[action['location']][3] + action['energy']
                        # if no more energy, kill
                        if self.dict[action['location']][3] < 1:
                            #dead.append(index)
                            del self.dict[action['location']]
                            #print(row['name'] + " starves.")

            ############
            # CHECKING END OF YEAR STATS
            ############

            # SAVE THE SNAPSHOT FOR PLOTTING
            if savePlotDF == True:
                thisYear = pd.DataFrame([[self.year] + [int(coord) for coord in x.split(',')] + [self.dict[x][0]] + [round(self.dict[x][3],1)] for x in self.dict.keys()], columns = plotCols)
                plotDF = plotDF.append(thisYear)

            critterCount = Counter([critter[1] for critter in self.dict.values() if (critter[1] != 'Rock')]) # used to have this too:  & (critter[1] != 'Plant')
            
            #print the critter count
            if yearlyPrinting == True:
                speciesCount = Counter([critter[0] for critter in self.dict.values() if (critter[1] != 'Rock')]) # used to have this too:  & (critter[1] != 'Plant')
                print('Year ' + str(self.year) + ': ' + str(speciesCount))
                '''
                #log count of each animal in yearStats
                for animal in self.bookOfLife.keys():
                    try:
                        count = critterCount[animal]
                    except:
                        count = 0
                    self.yearStats.append([self.year, count, animal])
                '''

            # log paramStats (make this every 10 years?)
            self.paramStats.append(self.getParamStats())


            #alert us if there's an extinction and log it in crakeStats
            if firstExt == False:
                if biomeCount != len(set([critter[0] for critter in self.dict.values() if critter[1] != 'Plant'])):
                    print('AN EXTINCTION!')
                    self.crakeStats[0] = self.year
                #reset it so that it doesn't keep tripping the conditional
                    firstExt = True
                    # if set to end the world at first extinction, then end it
                    if endOnExtinction == True:
                        break

            # IF AN ENDING CRITERIA IS SATISFIED, END THE WORLD 
                
                # 2a) if endOnOverflow==True: more than 10,000 critters total
                # 2b) if endOnOverflow==False: the RAREST species has more than 1,500 critters
                # 3) only plants (and rocks) left
            if (len(critterCount.keys()) < 1) | \
                ((endOnOverflow==True)&(sum(critterCount.values()) > 10000)) | \
                ((endOnOverflow==False)&(min(critterCount.values()) > 1500)) | \
                (all([key in ['Plant', 'Rock'] for key in critterCount.keys()])):
                # if everything is dead
                if (len(critterCount.keys()) < 1) | (all([key in ['Plant', 'Rock'] for key in critterCount.keys()])):
                    print('ITS A DEAD DEAD WORLD. Year ' + str(self.year))
                    # log the year the world ended
                    self.crakeStats[1] = self.year
                # if the world is too big
                if sum(critterCount.values()) > 10000:
                    print('THE CUP OVERFLOWETH. Year ' + str(self.year))
                    self.crakeStats[1] = number #'MAXLIFE50K'
                    # if there were no extinctions, set firstExt to MAX too
                    if self.crakeStats[0] == 1:
                        self.crakeStats[0] = number #'MAXLIFE50K'

                if saveYearStats == True:
                    # save the stats to csv       
                    paramDF = pd.DataFrame(self.paramStats, columns = self.paramCols)
                    if savePlotDF == True:
                        paramDF.to_csv('plotData/paramStats-' + str(epochNum) + '.csv', index=False)
                    else:
                        paramDF.to_csv('testData/YearStats/paramStats-' + self.id + '.csv', index=False)

                if savePlotDF == True:
                    print('%%%%%%%%\n%%%%%%%%\nSAVING plotDF\nplotDF-' + str(epochNum) + '\n%%%%%%%%\n%%%%%%%%')
                    plotDF.to_csv('plotData/plotDF-' + str(epochNum) + '.csv', index=False)


                # return year the world ended (and the first extinction)
                print(self.crakeStats)
                return(self.crakeStats)

        
        #########
        # IF IT RAN ALL THE WAY THROUGH...
        #########
        if saveYearStats == True:
            # save the stats to csv       
            paramDF = pd.DataFrame(self.paramStats, columns = self.paramCols)
            if savePlotDF == True:
                paramDF.to_csv('plotData/paramStats-' + str(epochNum) + '.csv', index=False)
            else:
                paramDF.to_csv('testData/YearStats/paramStats-' + self.id + '.csv', index=False)


        if savePlotDF == True:
            print('%%%%%%%%\n%%%%%%%%\nSAVING plotDF\nplotDF-' + str(epochNum) + '\n%%%%%%%%\n%%%%%%%%')
            plotDF.to_csv('plotData/plotDF-' + str(epochNum) + '.csv', index=False)

        # if there were no extinctions, set firstExt to this year
        if self.crakeStats[0] == 1:
            self.crakeStats[0] = self.year
        # set end of world to this year
        self.crakeStats[1] = self.year
        # return year the world ended (and the first extinction)
        print(self.crakeStats)
        return self.crakeStats



directions = {
    'nw':np.array([-1,1]),
    'n':np.array([0,1]),
    'ne':np.array([1,1]),
    'w':np.array([-1,0]),
    'e':np.array([1,0]),
    'sw':np.array([-1,-1]),
    's':np.array([0,-1]),
    'se':np.array([1,-1])
}


class View:
    def __init__(self, worldDict, coords):
        #self.lat = lat
        #self.long = long
        self.coords = np.array(coords)
        #self.critter = critter
        self.mydir = {}
        for key in directions:
            self.mydir[key] = directions[key] + self.coords
        # subset to adjacent spaces
        #self.df = world[world['lat'].between(lat - 1, lat + 1) & world['long'].between(long - 1, long + 1)]
        self.neighbors = {}
        self.spaces = []
        neighborhood = [x.tolist() for x in self.mydir.values()]
        for coord in neighborhood:
            thiskey = ",".join([str(x) for x in coord])
            try:
                self.neighbors[thiskey] = worldDict[thiskey]
            except:
                self.spaces = self.spaces + [thiskey]

        '''
        # store info about where critter is and what its energy is
        self.meHereNow = self.df[((lat == self.df['lat']) & (long == self.df['long']))]
        #get rid of where critter is actually standing (critter itself)
        self.df = self.df[~ ((lat == self.df['lat']) & (long == self.df['long'])) ]
        '''
        #(do we need this?)
        # store the name of world
        #self.world = world
        # start looking in a random direction 
        #self.direction = random.choice(list(directions.keys()))
        #

        
    
    #def location (self):
    #    return self.coords
    
    def look(self, lookDir):
        newcoords = self.coords + directions[lookDir]
        print('I am at ' + str(self.coords) + ' and looking ' + lookDir + ' I see ' + str(newcoords))
        see = self.df[(newcoords.tolist()[0] == self.df['lat']) & (newcoords.tolist()[1] == self.df['long'])]
        print(see)

    # look at whatever random direction you're facing (we may scrap this later)
    def blindLook(self):
        newcoords = self.coords + directions[self.direction]
        print('I am at ' + str(self.coords) + ' and looking ' + self.direction + ' I see ' + str(newcoords))
        see = self.df[(newcoords.tolist()[0] == self.df['lat']) & (newcoords.tolist()[1] == self.df['long'])]
        print(see)
    
    def find(self, search):
        found = self.df[self.df['kingdom'] == search]
        print('found ' + str(len(found.index)) + ' ' + search)
        print(found)
    
    '''
    def findSpace(self):
        cuts = []
        spaces = self.mydir
        # go through and identify which directions are occupied and save them in cuts
        for key in spaces:
            spot = spaces[key]
            for index, row in self.df.iterrows(): 
                if (spot[0] == row['lat']) & (spot[1] == row['long']):
                    cuts.append(key)
            #if (spot[0] in df['lat']) & (spot[0] in df['long'])
            #    cuts.append(key)
        # cut the occupied directions from spaces
        cuts = set(cuts)
        for cut in cuts:
            del spaces[cut]
        return spaces
        '''
