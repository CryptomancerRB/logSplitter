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

creator.create("Fitness", base.Fitness, weights=(-1.0, 1.0))
creator.create("Individual", set, fitness=creator.Fitness)

toolbox = base.Toolbox()

# Attribute generator
toolbox.register("attr_item", random.randrange, NBR_ITEMS)
toolbox.register("boardSet", makeBoardSet, myLog)

# Structure initializers
toolbox.register("individual", tools.initIter, creator.Individual, toolbox.boardSet)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)


def makeBoardSet(log):
    boardType = random.choice(items)
    sideways = random.randint(0,1)
    if(sideways == 1):
        TEMP = boardType[0]
        boardType[0] = boardType[1]
        boardType[1] = TEMP
    boardPos = [random.randint(MAX_SIZE-boardType[0]),
                random.randint(MAX_SIZE-boardType[1]),
                random.randint(LOG_LEN-boardType[2])]
    board = boardPos+boardType
    boardCenter = []
    boardCenter.append(board[X]+(board[W]/2)
    boardCenter.append(board[Y]+(board[H]/2)
    boardCenter.append(board[Z]+(board[D]/2)
    logCenter = midpoint(log,boardCenter[2])
    dirX = 1 if (boardCenter[X] < logCenter[X]) else -1
    dirY = 1 if (boardCenter[Y] < logCenter[Y]) else -1

    while not boardInLog(board,log):
        if math.abs(boardCenter[X] - logCenter[X]) > math.abs(boardCenter[Y] - logCenter[Y]):
            board[X] += dirX
            boardCenter[X] += dirX
        else:
            board[Y] += dirY
            boardCenter[Y] += dirX
    
    return [board]

def boardInLog(board,log):
    for f in range(board[Z],board[Z]+board[D]+1):
        for r in range(board[Y],board[Y]+board[H]+1):
            for c in range(board[X],board[X]+board[W]+1):
                if log[f][r][c] == 0:
                    return False
    return True

def evalKnapsack(individual):
    weight = 0.0
    value = 0.0
    for item in individual:
        weight += items[item][0]
        value += items[item][1]
    if len(individual) > MAX_ITEM or weight > MAX_WEIGHT:
        return 10000, 0             # Ensure overweighted bags are dominated
    return weight, value

def cxSet(ind1, ind2):
    """Apply a crossover operation on input sets. The first child is the
    intersection of the two sets, the second child is the difference of the
    two sets.
    """
    temp = set(ind1)                # Used in order to keep type
    ind1 &= ind2                    # Intersection (inplace)
    ind2 ^= temp                    # Symmetric Difference (inplace)
    return ind1, ind2
    
def mutSet(individual):
    """Mutation that pops or add an element."""
    if random.random() < 0.5:
        if len(individual) > 0:     # We cannot pop from an empty set
            individual.remove(random.choice(sorted(tuple(individual))))
    else:
        individual.add(random.randrange(NBR_ITEMS))
    return individual,

toolbox.register("evaluate", evalKnapsack)
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
