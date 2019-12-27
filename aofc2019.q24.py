# python3

# 24)

import copy
import itertools
import collections

BUG = '#'
SPACE = '.'

nth_tile = lambda y,x,leny: 2**(((y*leny)+(x+1))-1)

def count_bugs(grid, y, x, leny, lenx):
    bugs = 0
    if y-1 >= 0   and grid[y-1][x] == BUG: bugs += 1
    if y+1 < leny and grid[y+1][x] == BUG: bugs += 1
    if x-1 >= 0   and grid[y][x-1] == BUG: bugs += 1
    if x+1 < lenx and grid[y][x+1] == BUG: bugs += 1
    return bugs

# 2 jobs: (2) sum layout value for current grid and (2) create new grid: ngrid
# A bug dies (becoming an empty space) unless there is exactly one bug adjacent to it.
# An empty space becomes infested with a bug if exactly one or two bugs are adjacent to it.
def minute_passed(grid, leny, lenx):
    layout = 0
    ngrid = []
    for y in range(leny):
        nrow = ""
        for x in range(lenx):
            bugs = count_bugs(grid, y, x, leny, lenx)
            if grid[y][x] == BUG:
                layout += nth_tile(y, x, leny)
                if bugs != 1:
                    setbug = SPACE
                else:
                    setbug = BUG
            else:
                if bugs == 1 or bugs == 2:
                    setbug = BUG
                else:
                    setbug = SPACE
            nrow += setbug
        ngrid += [nrow]
    return layout, ngrid


def print_grid(grid):
    print ()
    for row in grid:
        print (row)

# for (b)
def count_gbugs(grid):
    return list(''.join(grid)).count(BUG)

def getcol(grid, leny, col):
    s = ''
    for y in range(leny):
        s += grid[y][col]
    return s

def count_bugs_inf(ogrid, grid, igrid, y, x, leny, lenx):
    bugs = 0
    if y-1 >= 0    and grid[y-1][x] == BUG: bugs += 1
    if y+1 < leny  and grid[y+1][x] == BUG: bugs += 1
    if x-1 >= 0    and grid[y][x-1] == BUG: bugs += 1
    if x+1 < lenx  and grid[y][x+1] == BUG: bugs += 1
    if y-1 < 0     and igrid[1][2]  == BUG: bugs += 1   # middle top
    if y+1 >= leny and igrid[3][2]  == BUG: bugs += 1   # middle bottom
    if x-1 < 0     and igrid[2][1]  == BUG: bugs += 1   # middle left
    if x+1 >= lenx and igrid[2][3]  == BUG: bugs += 1   # middle right
    if (y-1,x) == (2,2): bugs += list(ogrid[leny-1]).count(BUG)
    if (y+1,x) == (2,2): bugs += list(ogrid[0]).count(BUG)
    if (y,x-1) == (2,2): bugs += list(getcol(ogrid, leny, lenx-1)).count(BUG)
    if (y,x+1) == (2,2): bugs += list(getcol(ogrid, leny, 0)).count(BUG)        
    return bugs

def set_tile(ogrid, grid, igrid, y, x, leny, lenx):
    if (y,x) == (2,2):
        return SPACE
    bugs = count_bugs_inf(ogrid, grid, igrid, y, x, leny, lenx)
    if grid[y][x] == BUG:
        if bugs != 1:
            setbug = SPACE
        else:
            setbug = BUG
    else:
        if bugs == 1 or bugs == 2:
            setbug = BUG
        else:
            setbug = SPACE
    return setbug

def minute_passed_inf(infgrids, centre, leny, lenx):
    ogrid = infgrids[centre-1]
    grid  = infgrids[centre]
    igrid = infgrids[centre+1]
    ngrid = []
    for y in range(leny):
        nrow = ""
        for x in range(lenx):
            nrow += set_tile(ogrid, grid, igrid, y, x, leny, lenx)
        ngrid += [nrow]
    return ngrid

def print_gcounts(minute, infgrids):
    counts = []
    for grid in infgrids:
        counts += [count_gbugs(grid)]
    print ('%d) counts = %s, total = %d'%(minute, str(counts), sum(counts)))
    return sum(counts)

def print_grids(infgrids, leny):
    for y in range(leny):
        disp = ""
        for g in range(len(infgrids)):
            disp += infgrids[g][y]+" "
        print (disp)
    print ()
        
def advent24a(grid):
    leny = len(grid)
    lenx = len(grid[0])
    layouts = []
    layout = -1
    #print_grid(grid)
    for minute in itertools.count():
        layout, ngrid = minute_passed(grid, leny, lenx)
        #print (layout,'in',layouts)
        if layout in layouts:
            print_grid(grid)
            break
        else:
            layouts += [layout]
        grid = ngrid
    return layout

def advent24b(grid, initgrid, mins=999):
    leny = len(grid)
    lenx = len(grid[0])
    tgrids = collections.deque([grid])   # always without outermost/innermost initgrid
    centre = 1
    #print ("init")
    #print_grids(tgrids, leny)
    #for minute in itertools.count():
    for minute in range(mins):
        fgrids = collections.deque(copy.deepcopy(tgrids))
        fgrids.extendleft([copy.deepcopy(initgrid)])
        fgrids.extend([copy.deepcopy(initgrid)])

        ngrid = minute_passed_inf(fgrids, centre, leny, lenx)
        tgrids = collections.deque([ngrid])   # always without outermost/innermost initgrid

        outer = centre
        while outer-1 > 0 or count_gbugs(fgrids[outer]) > 0:
            if outer-1 == 0:
                fgrids.extendleft([copy.deepcopy(initgrid)])
                centre += 1
            else:
                outer -= 1
            ngrid = minute_passed_inf(fgrids, outer, leny, lenx)
            tgrids.extendleft([ngrid])

        inner = centre
        while inner+2 < len(fgrids) or count_gbugs(fgrids[inner]) > 0:
            inner += 1
            if inner+1 == len(fgrids):
                fgrids.extend([copy.deepcopy(initgrid)])
            ngrid = minute_passed_inf(fgrids, inner, leny, lenx)
            tgrids.extend([ngrid])

    bugs = print_gcounts(minute+1, tgrids)
    print_grids(tgrids, leny)
    return bugs

eg1 = '''
....#
#..#.
#..##
..#..
#....
'''

igrid = '''
.....
.....
.....
.....
.....
'''

advent24grid = '''
..#..
##..#
##...
#####
.#.##
'''

print (advent24a(eg1.splitlines()[1:]))  # 2129920
print ("24) answer part (a):", advent24a(advent24grid.splitlines()[1:])) # 2130474
print ()
print (advent24b(eg1.splitlines()[1:], igrid.splitlines()[1:], mins=10)) # 99 bugs
print ("24) answer part (b):", advent24b(advent24grid.splitlines()[1:], igrid.splitlines()[1:], mins=200)) # 1923
