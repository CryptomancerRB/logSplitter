import random
import numpy as np

MIN_SED = 8
MAX_SED = 12
LOG_LEN = 192
MAX_SIZE = 24

def nextCross(prev):
    cross = [[0 for c in range(MAX_SIZE)] for r in range(MAX_SIZE)] 
    minY = MAX_SIZE
    minX = MAX_SIZE
    maxY = 0
    maxX = 0
    for r in range(MAX_SIZE):
        for c in range (MAX_SIZE):
            if prev[r][c] == 1:
                if r < minY and r > 0:
                    minY = r
                if r > maxY and r<MAX_SIZE:
                    maxY = r
                if c < minX and c > 0:
                    minX = c
                if c > maxX and c<MAX_SIZE:
                    maxX = c
    midpointX = int((float(maxX+minX+random.randint(0,1)))/2.0)
    midpointY = int((float(maxY+minY+random.randint(0,1)))/2.0)
    radius = int(((maxX-minX)+(maxY-minY))/4)
    if(radius < MIN_SED/2):
        radius = (MIN_SED/2) + 1
    if(radius > MAX_SED/2):
        radius = (MAX_SED/2) - 1
    print(minY,maxY,minX,maxX,radius)
    for r in range(MAX_SIZE):
        for c in range (MAX_SIZE):
            manhatten = abs(midpointX-c) + abs(midpointY-r)
            manhatten -= random.randint(0,1);
            if manhatten <= radius:
                cross[r][c] = 1

    print(midpointY,midpointX)
    print("_"*MAX_SIZE)
    for r in range(MAX_SIZE):
        print("|",end='')
        for c in range (MAX_SIZE):
            if cross[r][c] == 0:
                print(" ",end='')
            else:
                print("#",end='')
        print("|")
    print("_"*MAX_SIZE)
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
            manhatten -= random.randint(0,1);
            if manhatten < radius:
                cross[r][c] = 1
    print("_"*MAX_SIZE)
    for r in range(MAX_SIZE):
        print("|",end='')
        for c in range (MAX_SIZE):
            if cross[r][c] == 0:
                print(" ",end='')
            else:
                print("#",end='')
        print("|")
    print("_"*MAX_SIZE)
    return cross


def makeLog():
    log = []
    minDiameter = random.randint(MIN_SED,MAX_SED)
    minEnd = initCross(minDiameter)
    log.append(minEnd)
    for z in range(0,LOG_LEN):
        log.append(nextCross(log[z]))
    rev = random.randint(0,1)
    if rev==1:
        log.reverse()


makeLog()
