import random

def nextCross(prev,gnarl):
    curr = [row[:] for row in prev]
    for r in range(1,len(prev)-1):
        for c in range(1,len(prev[0])-1):
            if(prev[r][c] == 1 and prev[r-1][c]+prev[r][c-1]+prev[r+1][c]+prev[r][c+1] <= 2):
                mutate = random.randint(0,gnarl)
                if(mutate==0):
                    curr[r][c] = 0
            elif(prev[r][c] == 0 and prev[r-1][c]+prev[r][c-1]+prev[r+1][c]+prev[r][c+1] >= 2):
                mutate = random.randint(0,gnarl)
                if(mutate==0):
                    curr[r][c] = 1
    return curr

         
end = [[0,0,0,0,0],
        [0,0,1,0,0],
        [0,1,1,1,0],
        [0,0,1,0,0],
        [0,0,0,0,0]]

next = nextCross(end,10)
for r in range(0,len(end)):
    print(end[r])
print()
for r in range(0,len(end)):
    print(next[r])


