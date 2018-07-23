#    This file is part of DEAP.
#
#    DEAP is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of
#    the License, or (at your option) any later version.
#
#    DEAP is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public
#    License along with DEAP. If not, see <http://www.gnu.org/licenses/>.

import random

import logArray

import numpy

import csv

import math

from deap import algorithms
from deap import base
from deap import creator
from deap import tools

# logArray.get_logArray.get_max_size()

IND_INIT_SIZE = 5
MAX_ITEM = 50
MAX_WEIGHT = 50
NBR_ITEMS = 0
X = 0
Y = 1
Z = 2
W = 3
H = 4
D = 5
V = 6
myLog = logArray.makeLog()

# To assure reproductibility, the RNG seed is set prior to the items
# dict initialization. It is also seeded in main().
random.seed(64)

# Create the item dictionary: item name is an integer, and value is 
# a (weight, value) 2-uple.
items = []
# Create random items and store them in the items' dictionary.
with open('boardData.csv', 'r') as csvfile:
    boardreader = csv.reader(csvfile, delimiter=',', quotechar='|')
    for row in boardreader:
        item = []
        item.append(int(row[0]))
        item.append(int(row[1]))
        item.append(int(row[2]))
        item.append(float(row[3]))
        items.append(item)
        NBR_ITEMS+=1

creator.create("Fitness", base.Fitness, weights=(1.0))
creator.create("Individual", set, fitness=creator.Fitness)

toolbox = base.Toolbox()

def makeBoardSet(log):
    for boardType in random.sample(items,len(items)):
        sideways = random.randint(0,1)
        if(sideways == 1):
            TEMP = boardType[0]
            boardType[0] = boardType[1]
            boardType[1] = TEMP
        boardPos = [random.randint(0, logArray.get_max_size()-boardType[0]),
                    random.randint(0, logArray.get_max_size()-boardType[1]),
                    random.randint(0, logArray.get_log_len()-boardType[2])]
        board = boardPos+boardType
        boardFitted = fitBoardInLog(board,myLog) 
        if boardFitted[0]:
            return [boardFitted[1]]

# Attribute generator
toolbox.register("attr_item", random.randrange, NBR_ITEMS)
toolbox.register("boardSet", makeBoardSet, myLog)

# Structure initializers
toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.boardSet)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

def overlap(Brd1, Brd2):
    c = 0
    for dim in range(3):
        if (((Brd1[dim] + Brd1[W+dim]) > Brd2[X]) and (Brd1[dim] < Brd2[dim] ) ) or ( (Brd1[dim] < (Brd2[dim] + Brd2[W+dim])) and (Brd1[dim] > Brd2[dim])): # If x overlaps
            c += 1
    return (True if c == 3 else False)

def fitBoardInLog(board,log):
    boardCenter = []
    boardCenter.append(int(round((board[X]+(board[W]/2)),0)))
    boardCenter.append(int(round((board[Y]+(board[H]/2)),0)))
    boardCenter.append(int(round((board[Z]+(board[D]/2)),0)))
    logCenter = logArray.midpoint(log,boardCenter[2])
    dirX = 1 if (boardCenter[X] < logCenter[X]) else -1
    dirY = 1 if (boardCenter[Y] < logCenter[Y]) else -1

    while not boardInLog(board,log):
        if abs(boardCenter[X] - logCenter[X]) >= abs(boardCenter[Y] - logCenter[Y]):
            board[X] += dirX
            boardCenter[X] += dirX
        else:
            board[Y] += dirY
            boardCenter[Y] += dirY
        if ((dirX == 1 and boardCenter[X] > logCenter[X]) or (dirX == -1 and boardCenter[X] < logCenter[X])) or ((dirY == 1 and boardCenter[Y] > logCenter[Y]) or (dirY == -1 and boardCenter[Y] < logCenter[Y])):
            return [False,[]]

        
    return [True,board]

def boardInLog(board,log):
    for f in range(board[Z],board[Z]+board[D]+1):
        for r in range(board[Y],board[Y]+board[H]+1):
            for c in range(board[X],board[X]+board[W]+1):
                if log[f][r][c] == 0:
                    return False
    return True

def evalSolution(individual):
    value = 0.0
    for item in individual:
        value += items[item][V]
    return value

def addBoards(baseBoards,newBoards):
    returnBoards = baseBoards.copy()
    for newBoard in newBoards:
        b = False
        for baseBoard in baseBoards:
            if overlap(newBoard, baseBoard):
                b = True
                break
        if b:
            returnBoards.append(newBoard)
    return returnBoards

def translate(log,individ,index,dir,axis):
    newBoard = individ.pop(index)
    while(boardInLog(newBoard,log)):
        newBoard[axis] += dir
        for i in range(len(individ)):
            if overlap(individ[i],newBoard):
                newBoard[axis] -= dir
                individ.append(newBoard)
                return individ
    newBoard[axis] -= dir
    individ.append(newBoard)
    return individ

def cxSet(ind1, ind2):
    """Apply a crossover operation on input sets. The first child is the
    intersection of the two sets, the second child is the difference of the
    two sets.
    """
    temp = ind1.copy()
    ind1 = addBoards(temp,ind2)
    ind2 = addBoards(ind2,temp)
    return ind1, ind2
    
def mutSet(individual):
    mutationSelected = random.random()
    dir = (2*random.randint(0,1))-1
    choice = random.randint(0,len(individual)-1)
    if mutationSelected < 0.3:
       individual = translate(myLog,individual,choice,dir,X) 
    elif mutationSelected < 0.6:
       individual = translate(myLog,individual,choice,dir,Y) 
    elif mutationSelected < 0.9:
       individual = translate(myLog,individual,choice,dir,Z) 
    else:
        individual.pop(choice)
    return individual

toolbox.register("evaluate", evalSolution)
toolbox.register("mate", cxSet)
toolbox.register("mutate", mutSet)
toolbox.register("select", tools.selNSGA2)

def main():
    random.seed(64)
    NGEN = 50
    MU = 50
    LAMBDA = 100
    CXPB = 0.7
    MUTPB = 0.2
    
    pop = toolbox.population(n=MU)
    hof = tools.ParetoFront()
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", numpy.mean, axis=0)
    stats.register("std", numpy.std, axis=0)
    stats.register("min", numpy.min, axis=0)
    stats.register("max", numpy.max, axis=0)
    
    algorithms.eaMuPlusLambda(pop, toolbox, MU, LAMBDA, CXPB, MUTPB, NGEN, stats,
                              halloffame=hof)
    
    return pop, stats, hof
                 
if __name__ == "__main__":
    main() 
