# python3

# 10)

import os
import math

def read_space(file):
    space = os.popen("cat "+file).read().split()
    return space

def make2d(sarr):
    arr2d = []
    for s in sarr:
        arr2d.append(list(s))
    return arr2d

def pspace(space):
    for row in space:
        print (row)

def swapdict(d):
    return dict([(v,k) for k,v in d.items()]) 

def get_asteroids(space):
    asts = set()
    for y in range(len(space)):
        for x in range(len(space[0])):
            if space[y][x] == '#':
                asts.add((x,y))  # use x first, the same order as the problem text
    return asts

# asteroid coords relative to a specific asteroid: {offset1:astrel, ...}
# all relationships (all (x,y) coords): {asteroid: {offset1:astrel, ...}}
def get_relationship(ast, asts):
    relship = {}
    for astrel in asts - set({ast}):
        relship[astrel] = (astrel[0]-ast[0], astrel[1]-ast[1])
    return relship
def get_relationships(asts):
    relships = {}
    for ast in asts:
        relships[ast] = get_relationship(ast, asts)
    return relships

def lfactor(x, y):
    while(y):
        x,y = y,x%y
    return x

def reduce_offset(x,y):
    lf = abs(lfactor(x,y))
    return int(x/lf), int(y/lf)

# include the near asteroid too
def remove_hidden(noff, ast, relship, xlen, ylen):
    xguess,yguess = ast[0],ast[1]
    xoff,yoff = reduce_offset(noff[0],noff[1])
    for i in range(max(xlen,ylen)):
        xguess += xoff
        yguess += yoff
        guess = (xguess,yguess)
        if guess in relship:
            del relship[guess]
    return relship

def count_visible(ast, relship, xlen, ylen):
    offset2ast = swapdict(relship)
    vast = set()
    while relship:
        noff = min(relship.values(), key=lambda t:(abs(t[0]),abs(t[1])))
        vast.add(offset2ast[noff])
        relship = remove_hidden(noff, ast, relship, xlen, ylen)
    return vast
def count_visibles(relships, xlen, ylen):
    vismap = {}
    for ast,relship in relships.items():
        vismap[ast] = count_visible(ast, relship, xlen, ylen)
    return vismap
        
def advent10a(space):
    space = make2d(space)
    xlen,ylen = len(space[0]), len(space)
    asts = get_asteroids(space)
    relships = get_relationships(asts)
    vismap = count_visibles(relships, xlen, ylen)
    maxvis = max(vismap.items(), key=lambda t: len(t[1]))
    return maxvis[0], len(maxvis[1])


# dsort_asteroids(ast, asts) degree sort
# 1. pass:   ast is the centre of the circle, asts are those asteroids to be hit by a laser
# 2. get:    relships {astrel:offset1, ...}   offset2ast {offset1:astrel, ...}
# 3. get:    degree_sort_asteroids returns a sorted (on degrees) dict {offset1:degrees, ...}
# 4. return: array of asteroid (absolute) locations is returned in order of lasering
def degree_sort_asteroids(offs):
    degmap = {}
    for off in offs:
        degmap[off] = math.atan2(off[0],off[1]) / math.pi * 180
    return dict(sorted(degmap.items(), key=lambda p: p[1], reverse=True))
def dsort_asteroids(ast, asts):
    relship = get_relationship(ast, asts)
    offset2ast = swapdict(relship)
    degmap = degree_sort_asteroids(relship.values())
    dsort_asts = []
    for off,deg in degmap.items():
        dsort_asts.append(offset2ast[off])
    return dsort_asts

def advent10b(space, zaps):
    space = make2d(space)
    xlen,ylen = len(space[0]), len(space)
    asts = get_asteroids(space)
    relships = get_relationships(asts)
    vismap = count_visibles(relships, xlen, ylen)
    maxvis = max(vismap.items(), key=lambda t: len(t[1]))
    laser,vasts = maxvis[0], maxvis[1]

    while zaps:
        if zaps > len(vasts):
            zaps -= len(zaps)
            asts -= vasts
            relship = get_relationship(laser, asts)
            vasts = count_visible(laser, relship, xlen, ylen)
        else:
            vasts = dsort_asteroids(laser, vasts)
            lasast = vasts[zaps-1]  # zaps-1 is the nth asteroid to be lasered
            return lasast, lasast[0]*100 + lasast[1]
    return None

eg1 = ['.#..#',
       '.....',
       '#####',
       '....#',
       '...##']
eg2 = ['......#.#.',
       '#..#.#....',
       '..#######.',
       '.#.#.###..',
       '.#..#.....',
       '..#....#.#',
       '#..#....#.',
       '.##.#..###',
       '##...#..#.',
       '.#....####']
eg3 = ['#.#...#.#.',
       '.###....#.',
       '.#....#...',
       '##.#.#.#.#',
       '....#.#.#.',
       '.##..###.#',
       '..#...##..',
       '..##....##',
       '......#...',
       '.####.###.']
eg4 = ['.#..##.###...#######',
       '##.############..##.',
       '.#.######.########.#',
       '.###.#######.####.#.',
       '#####.##.#.##.###.##',
       '..#####..#.#########',
       '####################',
       '#.####....###.#.#.##',
       '##.#################',
       '#####.##.###..####..',
       '..######..##.#######',
       '####.##.####...##..#',
       '.#####..#.######.###',
       '##...#.##########...',
       '#.##########.#######',
       '.####.#.###.###.#.##',
       '....##.##.###..#####',
       '.#.#.###########.###',
       '#.#.#.#####.####.###',
       '###.##.####.##.#..##']
advent10a_file = "advent10a.txt"

print (advent10a(eg1))  # (3,4), 8
print (advent10a(eg2))  # (5,8), 33
print (advent10a(eg3))  # (1,2), 35
print (advent10a(eg4))  # (11,13), 210
print ("10) answer part (a):", advent10a(read_space(advent10a_file))) # (29,28), 256

print (advent10b(eg4, 200))  # (8,2), 802
print ("10) answer part (b):", advent10b(read_space(advent10a_file), 200)) # (17, 7), 1707
