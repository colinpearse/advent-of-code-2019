# python3

# 20)

# NOTE: pop(0) and collections.deque.popleft() doesn't do what heapq.heappop() does - find out why

import re
import os
import sys
import heapq

LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

def is_path(c):
   return c == '.'
def is_gate(c):
   return c in LETTERS

def y_corridor(maze, y, x, width):
    return (x == 1 or maze[y][x-1] == '#') and (x == width-2 or maze[y][x+1] == '#')
def x_corridor(maze, y, x, height):
    return (y == 1 or maze[y-1][x] == '#') and (y == height-2 or maze[y+1][x] == '#')
def y_ok2go(maze, y, x, width):
    return is_path(maze[y][x]) and y_corridor(maze, y, x, width)
def x_ok2go(maze, y, x, height):
    return is_path(maze[y][x]) and x_corridor(maze, y, x, height)

def add_paths(steps, y, x, copygates, hasbeens, paths):
    been = (y, x, str(copygates))
    if been not in hasbeens:
        hasbeens.add(been)
        heapq.heappush(paths, (steps+1, y, x, copygates))

def do_steps(maze, gates1, gates2, steps, y, x, oldy, oldx, gates, hasbeens, paths):
    steps += abs(y-oldy) + abs(x-oldx) - 1
    c = maze[y][x]
    if is_path(c):
        copygates = gates[:]
        add_paths(steps, y, x, gates, hasbeens, paths)
    elif is_gate(c):
        pos=None
        if   maze[y+1][x] == '.': pos=(y+1,x)
        elif maze[y-1][x] == '.': pos=(y-1,x)
        elif maze[y][x+1] == '.': pos=(y,x+1)
        elif maze[y][x-1] == '.': pos=(y,x-1)
        copygates = gates[:]
        if pos in gates:
            y,x = pos
        else:
            if pos in gates1:
                y,x = gates1[pos]
                copygates += [pos,gates1[pos]]
            elif pos in gates2:
                y,x = gates2[pos]
                copygates += [pos,gates2[pos]]
        add_paths(steps, y, x, copygates, hasbeens, paths)

# don't search the edges
def get_gates(maze):
    height = len(maze)
    width = len(maze[0])
    gates1 = {}
    gates2 = {}
    for y in range(1,height-1):
        for x in range(1,width-1):
            c = maze[y][x]
            if c in LETTERS:
                pos = None; name = None
                if   maze[y+1][x] == '.': c1 = maze[y-1][x]; pos=(y+1,x); name=c1+c
                elif maze[y-1][x] == '.': c2 = maze[y+1][x]; pos=(y-1,x); name=c+c2
                elif maze[y][x+1] == '.': c1 = maze[y][x-1]; pos=(y,x+1); name=c1+c
                elif maze[y][x-1] == '.': c2 = maze[y][x+1]; pos=(y,x-1); name=c+c2
                if pos != None:
                    if name not in gates1:
                        gates1[name] = pos  # temp pos, except AA and ZZ
                    else:
                        tmpy,tmpx           = gates1[name]
                        gates2[pos]         = (tmpy,tmpx)
                        gates1[(tmpy,tmpx)] = pos
                        if name != 'AA' and name != 'ZZ':
                            del gates1[name]
    return gates1, gates2

# for (b) I need to differentiate between outer and inner gates
# outer points to inner and vice versa; also AA,ZZ both in outer
def convert_gates(gates1, gates2, height, width):
    igates = {}
    ogates = {}
    for gates in gates1, gates2:
        for y,x in gates:
            if y == 'A' or y == 'Z':
                ogates[y+x] = gates[y+x]
            elif  y>2 and y<height-3 and x>2 and x<width-3:
                igates[(y,x)] = gates[(y,x)]
            else:
                ogates[(y,x)] = gates[(y,x)]
    return ogates, igates

def getgname(maze, y, x):
    name = None
    if   is_gate(maze[y-1][x]): name=maze[y-2][x]+maze[y-1][x]
    elif is_gate(maze[y+1][x]): name=maze[y+1][x]+maze[y+2][x]
    elif is_gate(maze[y][x-1]): name=maze[y][x-2]+maze[y][x-1]
    elif is_gate(maze[y][x+1]): name=maze[y][x+1]+maze[y][x+2]
    return name

# { gate:[outer,inner], ... }                    {(y,x):gate, ...}
# { 'AA':[(2,15),(-1,-1)], 'FG':[(2,11),(8,8)]   {(2,15):'AA', ...}
def make_gmaps(maze,gates1,gates2):
    gate2pos = {}
    pos2gate = {}
    for y,x in gates1:
        if y == 'A' or y == 'Z':
            gate = y+x
            y,x = gates1[gate]
            inner = (-1,-1)
        else:
            gate = getgname(maze,y,x)
            inner = gates1[(y,x)]
            pos2gate[inner] = gate
        gate2pos[gate] = [(y,x),inner]
        pos2gate[(y,x)] = gate
    for y,x in gates2:
        gate = getgname(maze,y,x)
        if gate2pos[gate][1] != (y,x):
            print ("ERROR: inner gate %s=(%d,%d), gate2pos has gate %s=(%s)"%(gate,y,x,gate,str(gate2pos[gate][1])))
    return gate2pos, pos2gate

def is_inner(pos, height, width):
    y,x = pos
    return y>2 and y<height-3 and x>2 and x<width-3

# should start [begin,end,1st,2nd,...,
def gate_seq(gates, height, width):
    gseq = "" 
    #for y,x in gates:
    #    if y>2 and y<height-3 and x>2 and x<width-3:
    for pos in gates:
        if is_inner(pos, height, width):
            gseq += 'i'
        else:
            gseq += 'o'
    return gseq

def move_around(maze, steps, y, x, height, width, gates1, gates2, gates, hasbeens, paths):
    oldy,oldx = y,x
    # UP
    y -= 1
    if y>=1 and maze[y][x] != '#':
        while y_ok2go(maze, y, x, width) and y>=1 and maze[y-1][x] != '#':
            y -= 1
        do_steps(maze, gates1, gates2, steps, y, x, oldy, oldx, gates, hasbeens, paths)
    y,x = oldy,oldx
    # DOWN
    y += 1
    if y<height-1 and maze[y][x] != '#':
        while y_ok2go(maze, y, x, width) and y<height-1 and maze[y+1][x] != '#':
            y += 1
        do_steps(maze, gates1, gates2, steps, y, x, oldy, oldx, gates, hasbeens, paths)
    y,x = oldy,oldx
    # LEFT
    x -= 1
    if x>=1 and maze[y][x] != '#':
        while x_ok2go(maze, y, x, height) and x>=1 and maze[y][x-1] != '#':
            x -= 1
        do_steps(maze, gates1, gates2, steps, y, x, oldy, oldx, gates, hasbeens, paths)
    y,x = oldy,oldx
    # RIGHT
    x += 1
    if x<width-1 and maze[y][x] != '#':
        while x_ok2go(maze, y, x, height) and x<width-1 and maze[y][x+1] != '#':
            x += 1
        do_steps(maze, gates1, gates2, steps, y, x, oldy, oldx, gates, hasbeens, paths)

def find_shortest_path(maze, gates1, gates2, begin, end):
    height = len(maze)
    width = len(maze[0])
    by,bx = begin
    ey,ex = end
    paths  = [[0, by, bx,     list([(by,bx),(ey,ex)])]]
    hasbeens = { (by, bx, str(list([(by,bx),(ey,ex)]))) }
    rsteps = -1
    while paths:
        steps, y, x, gates = heapq.heappop(paths)
        sys.stdout.write('%d %d \r'%(steps, len(paths)))
        if (y == ey and x == ex):
            rsteps = steps-1
            paths = []
        else:
            move_around(maze, steps, y, x, height, width, gates1, gates2, gates, hasbeens, paths)
    return rsteps, gates

def go_in(a):
    return re.sub(r'(oi)*',r'',a) == ''
def go_out(a):
    return re.sub(r'(io)*',r'',a) == ''
def turn_out(a):
    return a == 'oo'
def turn_in(a):
    return a == 'ii'
def correct_order(gates):
    return gates[:1]+gates[2:]+gates[1:2]  # begin,end,middle -> begin,middle,end
def split_gates(a):
    return re.sub(r'.(..)-.(..)',r'\1,\2',a).split(',')

# get shortest routes between inner and outer gates only (it will produce routes via other gates but we won't bother with those)
# return eg. { oJA-iVV: 34, [(2,14),(8,7)], ... }
def get_g2gsteps(maze, gates1, gates2, pos2gate, height, width):
    allpos = set(pos2gate.keys())
    g2gsteps = {}
    for pos1 in allpos:
        for pos2 in allpos:
            if pos1 != pos2:
                rsteps,gates = find_shortest_path(maze, gates1, gates2, pos1, pos2)
                if rsteps > 0 and len(gates) == 2:
                    g1 = pos2gate[pos1]
                    g2 = pos2gate[pos2]
                    g1io = 'i' if is_inner(pos1, height, width) else 'o'
                    g2io = 'i' if is_inner(pos2, height, width) else 'o'
                    g2gsteps['%s%s-%s%s'%(g1io,g1,g2io,g2)] = (rsteps,gates)
                    #print ('%s%s-%s%s'%(g1io,g1,g2io,g2), pos1,pos2,rsteps,len(gates))
    return g2gsteps

# pgates are positions, including outer and inner positions of the same game, eg. [(2,15), (8,5)] could be both 'AE'
def add_sequence(gateio,  begin, end, steps, seq, pgates, pos2gate):
    ngates = []
    for pgate in pgates:
        ngate = pos2gate[pgate]
        if ngate not in ngates:
            ngates += [ngate]
    if begin not in gateio:
        gateio[begin] = {}
        if begin not in gateio:
            gateio[begin] = {}
    gateio[begin][end] = (steps, int(len(seq)/2), ngates)

# oioioi eg inward - each pair is up a (recursion) level
# ioioip eg outward - each pair is a return down a level
# oo     eg turning from inward to outward
# ii     eg turning from outward to inward
def get_inout_routes(g2gsteps, height, width, pos2gate):
    gin = {}
    gout = {}
    tin = {}
    tout = {}
    for gg,ggsteps in g2gsteps.items():
        steps,gates = ggsteps
        if steps > 0:
            gates = correct_order(gates)
            seq = gate_seq(gates, height, width)
            begin,end = split_gates(gg)
            if   go_in(seq):    add_sequence(gin,  begin, end, steps, seq, gates, pos2gate)
            elif go_out(seq):   add_sequence(gout, begin, end, steps, seq, gates, pos2gate)
            elif turn_in(seq):  add_sequence(tin,  begin, end, steps, seq, gates, pos2gate)
            elif turn_out(seq): add_sequence(tout, begin, end, steps, seq, gates, pos2gate)
    return gin,gout,tin,tout

# This is when we recurse without an change in direction
# TO DO: this is a hack - need to improve this
def bad_recursion(gates):
    recurs = False 
    if len(gates) > 5:
        somegates = ','.join(gates[-2:])
        strgates = ','.join(gates[:-2])
        if somegates in strgates and 'o' not in strgates and 'i' not in strgates:
            recurs = True 
    return recurs

# TO DO: been should check i/o and latest gate
def add_recpaths(steps, bgate, egate, inout, level, gates, hasbeens, paths, label="LABEL"):
    been = (egate, inout, level, ','.join(gates))
    #print ("%-3d %-8.8s: %s %-2.2d |%-5.5s|%-5.5s| gates(%s,%s):%s"%(steps, label, inout, level, (not bad_recursion(gates)), (been not in hasbeens), bgate, egate, ','.join(gates)))
    #input()
    if not bad_recursion(gates) and been not in hasbeens:
        hasbeens.add(been)
        heapq.heappush(paths, (steps+1, egate, inout, level, gates[:]))

# gin/gout/tin/tout is {begin:{end:(steps,levels)}} eg. {AA: {GV:(43,5), JE:(4,1), ...} ...}
def find_shortest_recursive_steps(gate2pos, pos2gate, gin, gout, tin, tout):
    paths  = [[0, 'AA', 'i', 0,     list(['AA','ZZ'])]]
    hasbeens = { ('AA', 'i', 0, str(list(['AA','ZZ']))) }
    rsteps = -1
    while rsteps == -1:
        steps, bgate, inout, level, gates = heapq.heappop(paths)
        sys.stdout.write('%d %d %d \r'%(steps, level, len(gates)))
        #print (steps, 'begin', bgate, inout, level, gates)
        #input()
        if bgate == 'ZZ' and level == 1:  # ZZ would bring it back to level 0
            #print (steps, inout, level, bgate, ','.join(gates))
            rsteps = steps-1
        else:
            if inout == 'i' and bgate in gin:
                for egate in gin[bgate]:
                    if egate != bgate and egate != 'AA':
                        chsteps,chlevel,ngates = gin[bgate][egate]
                        add_recpaths(steps+chsteps, bgate, egate, inout, level+chlevel, gates+ngates[1:], hasbeens, paths, label="INWARD")

            if inout == 'i' and bgate in tout:
                for egate in tout[bgate]:
                    if egate != bgate and egate != 'AA':
                        chsteps,chlevel,ngates = tout[bgate][egate]
                        add_recpaths(steps+chsteps, bgate, egate, 'o', level+chlevel, gates+['o']+ngates[1:], hasbeens, paths, label="TURN-OUT")

            if inout == 'o' and bgate in gout:
                for egate in gout[bgate]:
                    if egate != bgate and egate != 'AA':
                        chsteps,chlevel,ngates = gout[bgate][egate]
                        if level-chlevel >= 0:
                            add_recpaths(steps+chsteps, bgate, egate, inout, level-chlevel, gates+ngates[1:], hasbeens, paths, label="OUTWARD")

            if inout == 'o' and bgate in tin:
                for egate in tin[bgate]:
                    if egate != bgate and egate != 'AA':
                        chsteps,chlevel,ngates = tin[bgate][egate]
                        add_recpaths(steps+chsteps, bgate, egate, 'i', level-chlevel, gates+['i']+ngates[1:], hasbeens, paths, label="TURN-IN")
    return rsteps

def find_least_steps_a(maze):
    gates1,gates2 = get_gates(maze)
    steps, gates = find_shortest_path(maze, gates1, gates2, gates1['AA'], gates1['ZZ'])
    return steps

def find_least_steps_b(maze):
    height = len(maze)
    width = len(maze[0])
    gates1,gates2 = get_gates(maze)
    gates1,gates2 = convert_gates(gates1,gates2,height,width)  # 1-outer 2-inner
    gate2pos,pos2gate = make_gmaps(maze,gates1,gates2)
    g2gsteps = get_g2gsteps(maze, gates1, gates2, pos2gate, height, width)
    gin,gout,tin,tout = get_inout_routes(g2gsteps, height, width, pos2gate)
    return find_shortest_recursive_steps(gate2pos, pos2gate, gin, gout, tin, tout)
    
def readtext(file):
    return os.popen("cat "+file).read()

def advent20a(text="", filename=""):
    if text != "":
        return find_least_steps_a(text.splitlines()[1:])
    elif filename != "":
        return find_least_steps_a(readtext(filename).splitlines())

def advent20b(text="", filename=""):
    if text != "":
        return find_least_steps_b(text.splitlines()[1:])
    elif filename != "":
        return find_least_steps_b(readtext(filename).splitlines())

eg1 = '''
         A           
         A           
  #######.#########  
  #######.........#  
  #######.#######.#  
  #######.#######.#  
  #######.#######.#  
  #####  B    ###.#  
BC...##  C    ###.#  
  ##.##       ###.#  
  ##...DE  F  ###.#  
  #####    G  ###.#  
  #########.#####.#  
DE..#######...###.#  
  #.#########.###.#  
FG..#########.....#  
  ###########.#####  
             Z       
             Z       
'''
eg2 = '''
                   A               
                   A               
  #################.#############  
  #.#...#...................#.#.#  
  #.#.#.###.###.###.#########.#.#  
  #.#.#.......#...#.....#.#.#...#  
  #.#########.###.#####.#.#.###.#  
  #.............#.#.....#.......#  
  ###.###########.###.#####.#.#.#  
  #.....#        A   C    #.#.#.#  
  #######        S   P    #####.#  
  #.#...#                 #......VT
  #.#.#.#                 #.#####  
  #...#.#               YN....#.#  
  #.###.#                 #####.#  
DI....#.#                 #.....#  
  #####.#                 #.###.#  
ZZ......#               QG....#..AS
  ###.###                 #######  
JO..#.#.#                 #.....#  
  #.#.#.#                 ###.#.#  
  #...#..DI             BU....#..LF
  #####.#                 #.#####  
YN......#               VT..#....QG
  #.###.#                 #.###.#  
  #.#...#                 #.....#  
  ###.###    J L     J    #.#.###  
  #.....#    O F     P    #.#...#  
  #.###.#####.#.#####.#####.###.#  
  #...#.#.#...#.....#.....#.#...#  
  #.#####.###.###.#.#.#########.#  
  #...#.#.....#...#.#.#.#.....#.#  
  #.###.#####.###.###.#.#.#######  
  #.#.........#...#.............#  
  #########.###.###.#############  
           B   J   C               
           U   P   P               
'''
eg3 = '''
             Z L X W       C                 
             Z P Q B       K                 
  ###########.#.#.#.#######.###############  
  #...#.......#.#.......#.#.......#.#.#...#  
  ###.#.#.#.#.#.#.#.###.#.#.#######.#.#.###  
  #.#...#.#.#...#.#.#...#...#...#.#.......#  
  #.###.#######.###.###.#.###.###.#.#######  
  #...#.......#.#...#...#.............#...#  
  #.#########.#######.#.#######.#######.###  
  #...#.#    F       R I       Z    #.#.#.#  
  #.###.#    D       E C       H    #.#.#.#  
  #.#...#                           #...#.#  
  #.###.#                           #.###.#  
  #.#....OA                       WB..#.#..ZH
  #.###.#                           #.#.#.#  
CJ......#                           #.....#  
  #######                           #######  
  #.#....CK                         #......IC
  #.###.#                           #.###.#  
  #.....#                           #...#.#  
  ###.###                           #.#.#.#  
XF....#.#                         RF..#.#.#  
  #####.#                           #######  
  #......CJ                       NM..#...#  
  ###.#.#                           #.###.#  
RE....#.#                           #......RF
  ###.###        X   X       L      #.#.#.#  
  #.....#        F   Q       P      #.#.#.#  
  ###.###########.###.#######.#########.###  
  #.....#...#.....#.......#...#.....#.#...#  
  #####.#.###.#######.#######.###.###.#.#.#  
  #.......#.......#.#.#.#.#...#...#...#.#.#  
  #####.###.#####.#.#.#.#.###.###.#.###.###  
  #.......#.....#.#...#...............#...#  
  #############.#.#.###.###################  
               A O F   N                     
               A A D   M                     
'''
advent20a_file = 'aofc2019.20a.txt'

print ('shortest', advent20a(text=eg1))  # 23
print ('shortest', advent20a(text=eg2))  # 58
print ('20) a) shortest', advent20a(filename=advent20a_file)) # 714
print ()
print ('shortest', advent20b(text=eg3))  # 396
print ('20) b) shortest', advent20b(filename=advent20a_file)) # 7876
