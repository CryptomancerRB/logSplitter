import random

import logArray

import numpy

import csv

import math
import time

from deap import algorithms
from deap import base
from deap import creator
from deap import tools

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

random.seed()

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

    
def mutList(individual):
    prev = individual.copy()
    mutationSelected = random.random()
    dir = (2*random.randint(0,1))-1
    if len(individual)==0:
        return creator.Individual(individual)
    choice = random.randint(0,len(individual)-1)
    if mutationSelected < 0.3:
        individual = translate(myLog,individual,choice,dir,X) 
    elif mutationSelected < 0.6:
        individual = translate(myLog,individual,choice,dir,Y) 
    elif mutationSelected < 0.9 and len(individual)>1:
        individual = translate(myLog,individual,choice,dir,Z) 
    else:
        temp = individual.copy()
        newBoard = toolbox.individual()
        temp = addBoards(newBoard,temp)
        if evalSolution(temp) > evalSolution(individual):
            individual = temp.copy()
    return creator.Individual(individual)

toolbox.register("evaluate", evalSolution)
toolbox.register("mate", cxList)
toolbox.register("mutate", mutList)
toolbox.register("select", tools.selNSGA2)

def main():

    start_time = time.time()

    NGEN = 100
    MU = 100
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
                offspring[i], offspring[i+1] = toolbox.mate(child1,child2)
            i = i + 1

	# Apply mutation on the offspring
        for mutant in offspring:
            if random.random() < MUTPB:
                mutant = toolbox.mutate(mutant)
                #del mutant.fitness.values

	# The population is entirely replaced by the offspring
        pop[:] = offspring
        offspring.sort(key=lambda x: toolbox.evaluate(x)[0],reverse=True)
    hof = []

    print("--- %s seconds ---" % (time.time() - start_time))

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

                 
if __name__ == "__main__":
    main() 
