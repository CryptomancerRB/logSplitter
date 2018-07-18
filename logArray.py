import random
import numpy as np

MIN_SED = 8
MAX_SED = 12
LOG_LEN = 192
MAX_SIZE = 24

def nextCross(prev,minD):
    radius = int(diameter/2)
    cross = [[0 for c in range(MAX_SIZE)] for r in range(MAX_SIZE)] 
    minY = MAX_SIZE
    minX = MAX_SIZE
    maxY = 0
    maxX = 0
    for r in range(MAX_SIZE):
        for c in range (MAX_SIZE):
            if prev[r][c] == 1:
                if r < minY:
                    minY = r
                if r > maxY:
                    maxY = r
                if c < minX:
                    minX = c
                if c > maxX:
                    maxX = c
    midpointX = int((maxX+minX)/2)
    midpointY = int((maxY+minY)/2)
    radius = int(((maxX-minX)+(maxY-minY))/2)
    for r in range(MAX_SIZE):
        for c in range (MAX_SIZE):
            manhatten = abs(midpointX-c) + abs(midpointY-r)
            manhatten += 1
            manhatten -= random.randint(0,2);
            if manhatten < radius:
                cross[r][c] = 1

    print("__"*MAX_SIZE)
    for r in range(MAX_SIZE):
        print("|",end='')
        for c in range (MAX_SIZE):
            if cross[r][c] == 0:
                print("  ",end='')
            else:
                print("##",end='')
        print("|")
    print("__"*MAX_SIZE)
    return cross

def initCross(diameter):
    radius = int(diameter/2)
    cross = [[0 for c in range(MAX_SIZE)] for r in range(MAX_SIZE)] 
    midpointX = random.randint(4+(radius),MAX_SIZE-4-(radius))
    midpointY = random.randint(4+(radius),MAX_SIZE-4-(radius))
    print(midpointY,midpointX)
    for r in range(MAX_SIZE):
        for c in range (MAX_SIZE):
            manhatten = abs(midpointX-c) + abs(midpointY-r)
            manhatten += 1
            manhatten -= random.randint(0,2);
            if manhatten < radius:
                cross[r][c] = 1
    print("__"*MAX_SIZE)
    for r in range(MAX_SIZE):
        print("|",end='')
        for c in range (MAX_SIZE):
            if cross[r][c] == 0:
                print("  ",end='')
            else:
                print("##",end='')
        print("|")
    print("__"*MAX_SIZE)
    return cross


def makeLog():
    log = np.array[]
    minDiameter = random.randint(MIN_SED,MAX_SED)
    minEnd = initCross(minDiameter)
    log.append(minSlice)
    for z in range(1,LOG_LEN):
        log.append(nextCross(log[z],minDiameter)
    rev = random.randint(0,1)
    if rev==1:
        log.reverse()


makeLog()
