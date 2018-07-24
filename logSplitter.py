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

creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)

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
            board = boardFitted[1]
            return creator.Individual(board)

# Attribute generator
#toolbox.register("attr_item", random.randrange, NBR_ITEMS)
toolbox.register("boardSet", makeBoardSet, myLog)

# Structure initializers
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.boardSet, 1)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

def overlapping(Brd1,Brd2,dim):
    if Brd1[dim] <= Brd2[dim] and Brd1[dim]+Brd1[dim+W] > Brd2[dim]:
        return True
    else:
        return False


def overlap(Brd1, Brd2):
    c = 0
    for dim in range(3):
        if overlapping(Brd1,Brd2,dim) or overlapping(Brd2,Brd1,dim):
            c += 1
    if c==3:
        return True
    else:
        return False

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
        value += item[V]
    return (value, 0)

def addBoards(baseBoards,newBoards):
    returnBoards = baseBoards.copy()
    for newBoard in newBoards:
        addBoard = True
        for baseBoard in baseBoards:
            if overlap(newBoard, baseBoard):
                addBoard = False
                break
        if addBoard:
            returnBoards.append(newBoard)
    return returnBoards

def translate(log,individual,index,dir,axis):
    individ = individual.copy()
    newBoard = individ.pop(index)
    while(boardInLog(newBoard,log)):
        newBoard[axis] += dir
        for i in range(len(individ)):
            if overlap(individ[i],newBoard):
                newBoard[axis] -= dir
                individ.append(newBoard)
                return individ
        if newBoard[axis] < 0 or (axis == Z and newBoard[axis]+newBoard[D] >= logArray.get_log_len()) or (axis != Z and newBoard[axis]+newBoard[3+axis] >= logArray.get_max_size()):
            break

    newBoard[axis] -= dir
    individ.append(newBoard)
    return individ

def cxList(ind1, ind2):
    temp = ind1.copy()
    ind1 = addBoards(temp,ind2)
    ind2 = addBoards(ind2,temp)
    return creator.Individual(ind1), creator.Individual(ind2)
    #return creator.Individual(temp), creator.Individual(temp)

    
def mutList(individual):
    mutationSelected = random.random()
    dir = (2*random.randint(0,1))-1
    if len(individual)==0:
        return (creator.Individual(individual),)
    choice = random.randint(0,len(individual)-1)
    #print(dir,choice,mutationSelected)
    #print(individual)
    if mutationSelected < 0.33:
       individual = translate(myLog,individual,choice,dir,X) 
    elif mutationSelected < 0.66:
       individual = translate(myLog,individual,choice,dir,Y) 
    elif mutationSelected < 0.99:
       individual = translate(myLog,individual,choice,dir,Z) 
    else:
        individual.pop(choice)
    return (creator.Individual(individual),)

toolbox.register("evaluate", evalSolution)
toolbox.register("mate", cxList)
toolbox.register("mutate", mutList)
toolbox.register("select", tools.selNSGA2)

def main():
    random.seed(64)

    #NGEN = 50
    #MU = 50
    #LAMBDA = 100
    #CXPB = 0.7
    #MUTPB = 0.2

    NGEN = 10
    MU = 50
    LAMBDA = 1
    CXPB = 0.7
    MUTPB = 0.2
    
    pop = toolbox.population(n=MU)
    
    for g in range(NGEN):
	# Select the next generation individuals
        offspring = toolbox.select(pop, len(pop))

	# Clone the selected individuals
        offspring = list(map(toolbox.clone, offspring))

	# Apply crossover on the offspring
        i = 0
        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            if random.random() < CXPB:
                #child1,child2 = toolbox.mate(child1, child2)
                #del child1.fitness.values
                #del child2.fitness.values

                a,b =  toolbox.mate(child1,child2)
                offspring[i], offspring[i+1] = toolbox.mate(child1,child2)
                del child1.fitness.values
                del child2.fitness.values
            i = i + 1

	# Apply mutation on the offspring
        for mutant in offspring:
            if random.random() < MUTPB:
                toolbox.mutate(mutant)
                del mutant.fitness.values

	# Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

	# The population is entirely replaced by the offspring
        pop[:] = offspring
    hof = []
    for sol in pop:
        if(len(hof) < 3):
            hof.append(sol)
        else:
            for goodSol in hof:
                if toolbox.evaluate(sol) > toolbox.evaluate(goodSol):
                    hof.remove(goodSol)
                    hof.append(sol)
    hof.sort(key=lambda x: toolbox.evaluate(x)[0],reverse=True)
    for sol in hof:
        print()
        print("Score:",toolbox.evaluate(sol)[0])
        sol.sort(key=lambda x: x[V],reverse=True)
        for board in sol:
            print(board)

    #hof = tools.ParetoFront()
    #stats = tools.Statistics(lambda ind: ind.fitness.values)
    #stats.register("avg", numpy.mean, axis=0)
    #stats.register("std", numpy.std, axis=0)
    #stats.register("min", numpy.min, axis=0)
    #stats.register("max", numpy.max, axis=0)
    
    #algorithms.eaMuPlusLambda(pop, toolbox, MU, LAMBDA, CXPB, MUTPB, NGEN, stats, halloffame=hof)


    #ind1 = toolbox.individual()
    #print("ind1:",ind1)
    #mutant = toolbox.clone(ind1)
    #print("mut:",mutant)
    #ind2, = toolbox.mutate(mutant)
    #print("ind2:",ind2)
    #print("mut:",mutant)

    #return
    #print(pop)
    #for b in pop[0]:
        #print("X from",b[X],"to",b[X]+b[W],end='    ')
        #print("Y from",b[Y],"to",b[Y]+b[H],end='    ')
        #print("Z from",b[Z],"to",b[Z]+b[D])
    #MAX_SIZE = logArray.get_max_size()
    #print("_"*MAX_SIZE)
    #for r in range(MAX_SIZE):
        #print("|",end='')
        #for c in range (MAX_SIZE):
            #numbered = False
            #for i in range(len(pop[0])):
                #cross = pop[0][i]
                #if r>=cross[Y] and r<cross[Y] + cross[H] and c>=cross[X] and c<cross[X] + cross[W]:
                    #print(i,end='')
                    #numbered = True
            #if not numbered:
                #if myLog[85][r][c] == 0:
                    #print(" ",end='')
                #else:
                    #print("#",end='')
        #print("|")
    #print("_"*MAX_SIZE)
    #return pop, stats, hof
                 
if __name__ == "__main__":
    main() 
