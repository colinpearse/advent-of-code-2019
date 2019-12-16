# python3

# 15) run auto/manual on xterm; auto only on Jupyter

import sys
import tty
import termios
import pickle
import time

# some #defines  http://ascii-table.com/ansi-escape-sequences-vt-100.php
TERM_CLEAR_SCREEN = chr(27)+'[2j'
TERM_INIT_STATE   = chr(27)+'c'
TERM_CURS_HOME    = chr(27)+'[H'
TERM_CURS_UP      = chr(27)+'[A'
TERM_CURS_DOWN    = chr(27)+'[B'
TERM_CURS_LEFT    = chr(27)+'[D'
TERM_CURS_RIGHT   = chr(27)+'[C'
TERM_CLEAR_SEQ    = TERM_CLEAR_SCREEN+TERM_INIT_STATE+TERM_CURS_HOME

WALL   = '@'
START  = 'X'
OXYGEN = 'O'
PATH   = '.'
PLAYER = 'o'

# Very Large Matrix
class VLM:
    def __init__(self, minx=0, miny=0, maxx=0, maxy=0, defval=0):
        self.__m = {}
        self.__Dm = {}  # displayed matrix, unlike m it will include defval
        self.__defval = defval
        self.__minx = minx
        self.__miny = miny
        self.__maxx = maxx
        self.__maxy = maxy
        self.__clearscreen = TERM_CLEAR_SCREEN+TERM_INIT_STATE+TERM_CURS_HOME

    def __setminmax(self, pos):
        x,y = pos
        if x < self.__minx: self.__minx = x; self.__clearscreen = TERM_CLEAR_SEQ
        if y < self.__miny: self.__miny = y; self.__clearscreen = TERM_CLEAR_SEQ
        if x > self.__maxx: self.__maxx = x; self.__clearscreen = TERM_CLEAR_SEQ
        if y > self.__maxy: self.__maxy = y; self.__clearscreen = TERM_CLEAR_SEQ

    def __setitem__(self, pos, val):
        self.__setminmax(pos)
        if val == self.__defval:
            if pos in self.__m:
                del self.__m[pos]
        else:
            self.__m[pos] = val

    def __getitem__(self, pos):
        self.__setminmax(pos)
        return self.__m[pos] if pos in self.__m else self.__defval

    def mset(self, a, val):
        for pos in a:
            self.__setitem__(pos, val)

    def msetd(self, d, mapval={}):
        for pos,val in d.items():
            if len(mapval) > 0:
                self.__setitem__(pos, mapval[val])
            else:
                self.__setitem__(pos, val)

    # printm() helpers
    def __setminx(self, rev):
        return self.__maxx   if rev else self.__minx
    def __setminy(self, rev):
        return self.__maxy   if rev else self.__miny
    def __setmaxx(self, rev):
        return self.__minx-1 if rev else self.__maxx+1
    def __setmaxy(self, rev):
        return self.__miny-1 if rev else self.__maxy+1
    def __setincx(self, rev):
        return -1 if rev else 1
    def __setincy(self, rev):
        return -1 if rev else 1
    def __getc(self, pos):
        c = self.__getitem__(pos)
        if pos in self.__Dm and c == self.__Dm[pos]:
             c = TERM_CURS_RIGHT
        else:
             self.__Dm[pos] = c
        return c
    def __outputline(self, line, j):
        if j == "join":
            if set(line) == set([TERM_CURS_RIGHT]):
                sys.stdout.write(TERM_CURS_DOWN)
            else:
                print (''.join(list(map(str, line))))
        else:
            print (line)

    def printm(self, j="", revy=False, revx=False, message=""):
        self.__Dm = {}  # don't use display cache for now
        sys.stdout.write(self.__clearscreen)
        self.__clearscreen = TERM_CURS_HOME
        print('\n'+message+'\n')
        minx = self.__setminx(revx)
        miny = self.__setminy(revy)
        maxx = self.__setmaxx(revx)
        maxy = self.__setmaxy(revy)
        incx = self.__setincx(revx)
        incy = self.__setincy(revy)
        for y in range(miny, maxy, incy):
            line = []
            for x in range(minx, maxx, incx):
                line.append(self.__getc((x,y)))
            self.__outputline(line, j)
        sys.stdout.flush()

# Very Large Array
class VLA:
    def __init__(self, alen=0):
        self.__a = {}
        self.__defval = 0
        self.__alen = alen

    def __setalen(self, idx):
        if idx+1 > self.__alen: self.__alen = idx+1

    def __len__(self):
        return self.__alen

    def __setitem__(self, idx, val):
        self.__setalen(idx)
        if val == 0:
            if idx in self.__a:
                del self.__a[idx]
        else:
            self.__a[idx] = val

    def __getitem__(self, idx):
        self.__setalen(idx)
        return self.__a[idx] if idx in self.__a else self.__defval
    
class IntBox:
    def __init__(self, prog):
        self.__oprog = prog
        self.__reset()

    def __reset(self):
        self.__prog = VLA()
        for i in range(len(self.__oprog)):
            self.__prog[i] = self.__oprog[i]
        self.__i = 0
        self.__rbase = 0
            
    def __codes(self):
        code = "0000"+str(self.__prog[self.__i])
        opcode = int(code[-2:])
        m1 = int(code[-3:-2])
        m2 = int(code[-4:-3])
        m3 = int(code[-5:-4])
        #print ("run:",opcode,self.__prog[self.__i])
        return opcode,m1,m2,m3

    def __set(self, i, mode):
        if mode == 0:
            return i
        # immediate mode (1) will never apply to set
        elif mode == 2:
            return self.__rbase + i
        
    def __get(self, i, mode):
        if mode == 0:
            return self.__prog[i]
        elif mode == 1:
            return i
        elif mode == 2:
            return self.__prog[self.__rbase + i]
        
    def __getparams(self, n, inc=True):
        params = [self.__prog[self.__i+addi] for addi in range(1,n+1)]
        if inc == True:
            self.__i += n+1
        return params[0] if len(params) == 1 else params
    
    def modify(self, code):
        for i,val in code.items():
            self.__prog[i] = val

    # returns: code,output (code==0 means run has finished successfully, code==1 means waiting for input)
    def run(self, I):
        O = []
        Ii = 0
        while True:
            opcode,m1,m2,m3 = self.__codes()
            if opcode == 1:
                i1,i2,i3 = self.__getparams(3)
                self.__prog[self.__set(i3,m3)] = self.__get(i1,m1) + self.__get(i2,m2)
            elif opcode == 2:
                i1,i2,i3 = self.__getparams(3)
                self.__prog[self.__set(i3,m3)] = self.__get(i1,m1) * self.__get(i2,m2)
            elif opcode == 3:
                i1 = self.__getparams(1, inc=False)  # don't increment, just in case we have to wait for input
                if Ii < len(I):
                    self.__prog[self.__set(i1,m1)] = I[Ii]
                    Ii += 1
                else:
                    #print ('waiting for input')
                    return 1, O  # no input: freeze ops for this object by returning output
                self.__i += 2
            elif opcode == 4:
                i1 = self.__getparams(1)
                O.append(self.__get(i1,m1))
                #print('output:', O)
            elif opcode == 5:
                i1,i2 = self.__getparams(2, inc=False)
                self.__i = self.__get(i2,m2) if self.__get(i1,m1) else self.__i+3
            elif opcode == 6:
                i1,i2 = self.__getparams(2, inc=False)
                self.__i = self.__get(i2,m2) if not self.__get(i1,m1) else self.__i+3
            elif opcode == 7:
                i1,i2,i3 = self.__getparams(3)
                self.__prog[self.__set(i3,m3)] = 1 if self.__get(i1,m1) < self.__get(i2,m2) else 0
            elif opcode == 8:
                i1,i2,i3 = self.__getparams(3)
                self.__prog[self.__set(i3,m3)] = 1 if self.__get(i1,m1) == self.__get(i2,m2) else 0
            elif opcode == 9:
                i1 = self.__getparams(1)
                self.__rbase += self.__get(i1,m1)
            elif opcode == 99:
                self.__reset()
                return 0, O
            else:
                raise Exception(opcode)

def getinput():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    tty.setraw(sys.stdin.fileno())
    c = sys.stdin.read(1)
    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    move = 0
    if   c == 'i': move = 1  # up
    elif c == 'k': move = 2  # down
    elif c == 'j': move = 3  # left
    elif c == 'l': move = 4  # right
    return move

def gmove(gmap, ppos, spos, epos, move, result):
    x,y = ppos
    if   move == 1: y += 1
    elif move == 2: y -= 1
    elif move == 3: x -= 1
    elif move == 4: x += 1
    if   result == 0:
        pos = ppos
        gmap[(x,y)] = WALL
    elif result == 1:
        pos = (x,y)
        gmap[pos] = PLAYER
        gmap[ppos] = PATH
    elif result == 2:
        pos = (x,y)
        epos = pos
        gmap[pos] = OXYGEN
        gmap[ppos] = PATH
    if spos != None: gmap[spos] = START
    if epos != None: gmap[epos] = OXYGEN
    return gmap, ppos, pos, spos, epos

def gettype(gmap, c):
    return [k for k in gmap if gmap[k] == c]

def bestmove(gmap, pos, deadend):
    x,y = pos
    walls = set(gettype(gmap, WALL)) | set(gettype(gmap, START)) | set(gettype(gmap, OXYGEN))
    floor = set(gettype(gmap, PATH))
    dmoves = {(x,y+1):1, (x,y-1):2, (x-1,y):3, (x+1,y):4}
    pmoves = set(dmoves.keys())
    nmoves = pmoves - walls - floor
    if len(nmoves) == 0:
        deadend.add(pos)
        nmoves = pmoves - walls - deadend
    if len(nmoves) == 0:
        return -1, deadend
    else:
        nmove = list(nmoves)[0]
        return dmoves[nmove],deadend  # return 1, 2, 3 or 4

# functions to find all routes from START to OXYGEN
def possible_moves(gmap, pos):
    x,y = pos
    moves = []
    for newpos in (x,y-1),(x,y+1),(x-1,y),(x+1,y):
        if newpos in gmap and gmap[newpos] != WALL:
             moves.append(newpos)
    return moves

def get_paths(gmap, paths, end):
    more_moves = False
    for path in paths:
        if path[-1] == end:
            moves = []
        else:
            moves = possible_moves(gmap, path[-1])
            moves = list(set(moves) - set(path))
        if moves:
            more_moves = True
            fmove = moves.pop()
            for move in moves:
                paths += [path.copy()]
                paths[-1] += [move]
            path += [fmove]
    return paths, more_moves

def get_shortest_path(paths, begin, end):
    shortest = float("inf")
    for path in paths:
        if path[0] == begin and path[-1] == end:
            shortest = min(len(path), shortest)
    return shortest

def fewest_steps(mapfile):
    gmap = pickle.load(open(mapfile, "rb"))
    revmap = swapdict(gmap)
    begin = revmap[START]
    end = revmap[OXYGEN]
    paths = [[begin]]
    more_moves = True
    while more_moves:
        paths,more_moves = get_paths(gmap, paths, end)
    return get_shortest_path(paths, begin, end) - 1  # number of steps so does not include the starting square

def save_gmap(gmap, mapfile):
    fd = open(mapfile, "wb")
    pickle.dump(gmap, fd)
    fd.close()

# functions for (b)
def swapdict(d):
    return dict([(v,k) for k,v in d.items()]) 

def oxygen_can_fill(gmap, newpos):
    if newpos in gmap:
        if gmap[newpos] == PATH or gmap[newpos] == PLAYER or gmap[newpos] == START:
            return True
    return False

def get_moves(gmap, pos):
    x,y = pos
    moves = []
    for newpos in (x,y-1),(x,y+1),(x-1,y),(x+1,y):
        if oxygen_can_fill(gmap, newpos):
            moves.append(newpos)
    return moves
    
def new_moves(gmap, mpos):
    nmoves = []
    for pos in mpos:
        nmoves += get_moves(gmap, pos)
    return nmoves

def fill_with_oxygen(gmap, oxfill):
    for opos in oxfill:
        gmap[opos] = OXYGEN
    return gmap

# TERM_CURS_RIGHT default value of the matrix; the following values are mapped, see mapval:
# Input: 1,2,3,4 move up,down,left,right (N,S,W,E)
# Output:
# 0: hit a wall
# 1: moved
# 2: Oxygen found 
def advent15a(prog, mapfile, mode='manual', delay=0.1):
    comp = IntBox(prog)
    m = VLM(-3,-3,3,3,defval=TERM_CURS_RIGHT)
    spos = (0,0)
    epos = None
    pos = spos
    gmap = {pos:'o'}
    deadend = set()
    #fdlog = open("advent15.log", "w")
    distance = -1
    ret = -1
    I = []
    while True:
        if mode == 'auto':
            ic,deadend = bestmove(gmap,pos,deadend)
            if ic == -1:
                break
            I = [ic]
        else:
            I = [getinput()]
        time.sleep(delay)

        ret,O = comp.run(I)
        gmap, ppos, pos, spos, epos = gmove(gmap, pos, spos, epos, I[0], O[0])
        #print (I, O, ppos, pos, len(gmap), len(deadend), file=fdlog)
        m.msetd(gmap)
        m.printm(j='join', revy=True, message="JOYSTICK: i,k,j,l (up,down,left,right)  delay=%1.3f"%(delay))

    #fdlog.close()
    save_gmap(gmap, advent15savemap)
    steps = fewest_steps(advent15savemap)
    return steps

def advent15b(mapfile, mode='manual', delay=0.1, steps=-1):
    gmap = pickle.load(open(mapfile, "rb"))
    m = VLM(defval=TERM_CURS_RIGHT)
    revmap = swapdict(gmap)
    minutes = [[revmap[OXYGEN]]]
    while len(set(gmap.values())) != 2:
        minutes.append(new_moves(gmap, minutes[-1]))
        gmap = fill_with_oxygen(gmap, minutes[-1])
        m.msetd(gmap)
        m.printm(j='join', revy=True, message="15) answer part (a): %d  NOW FILL WITH OXYGEN  delay=%1.3f"%(steps, delay))
    return len(minutes)-1

advent15savemap = "advent15a.pkl"
advent15prog = [3,1033,1008,1033,1,1032,1005,1032,31,1008,1033,2,1032,1005,1032,58,1008,1033,3,1032,1005,1032,81,1008,1033,4,1032,1005,1032,104,99,101,0,1034,1039,102,1,1036,1041,1001,1035,-1,1040,1008,1038,0,1043,102,-1,1043,1032,1,1037,1032,1042,1106,0,124,1002,1034,1,1039,101,0,1036,1041,1001,1035,1,1040,1008,1038,0,1043,1,1037,1038,1042,1105,1,124,1001,1034,-1,1039,1008,1036,0,1041,1002,1035,1,1040,102,1,1038,1043,1001,1037,0,1042,1106,0,124,1001,1034,1,1039,1008,1036,0,1041,1001,1035,0,1040,1001,1038,0,1043,1001,1037,0,1042,1006,1039,217,1006,1040,217,1008,1039,40,1032,1005,1032,217,1008,1040,40,1032,1005,1032,217,1008,1039,1,1032,1006,1032,165,1008,1040,39,1032,1006,1032,165,1102,2,1,1044,1105,1,224,2,1041,1043,1032,1006,1032,179,1101,0,1,1044,1105,1,224,1,1041,1043,1032,1006,1032,217,1,1042,1043,1032,1001,1032,-1,1032,1002,1032,39,1032,1,1032,1039,1032,101,-1,1032,1032,101,252,1032,211,1007,0,45,1044,1106,0,224,1101,0,0,1044,1105,1,224,1006,1044,247,102,1,1039,1034,102,1,1040,1035,102,1,1041,1036,1001,1043,0,1038,1002,1042,1,1037,4,1044,1106,0,0,12,89,14,22,56,12,54,34,71,12,40,31,83,2,95,25,4,70,18,59,32,11,19,23,67,17,25,18,72,14,60,9,85,6,84,89,2,14,10,44,85,34,63,11,23,79,6,56,4,88,69,20,2,88,87,31,56,16,68,29,84,43,58,6,14,98,73,3,35,79,24,89,43,59,12,78,86,13,10,61,37,46,44,61,25,12,71,36,65,79,31,5,71,13,99,90,87,35,40,98,3,80,69,97,31,37,93,37,78,34,48,32,51,41,75,50,16,25,10,92,88,28,50,7,95,11,15,99,10,61,56,25,14,99,23,23,90,73,66,94,23,60,34,26,73,44,38,71,41,42,79,10,25,69,43,39,92,19,35,95,23,60,8,75,38,55,82,40,44,29,84,82,33,36,63,93,10,7,50,41,22,76,79,59,42,61,40,72,4,51,5,83,99,22,79,33,6,53,62,30,77,37,22,94,84,43,19,60,52,44,82,99,23,47,29,68,57,38,66,40,55,17,15,78,86,10,54,25,52,39,62,35,11,19,15,75,12,20,63,67,98,35,70,17,95,66,24,37,56,10,75,3,95,35,41,62,8,3,60,72,5,98,61,27,42,63,16,55,29,6,54,48,40,7,66,92,31,48,16,41,87,86,6,16,24,53,85,17,4,12,20,89,74,5,84,67,27,37,67,30,29,27,92,46,40,14,77,95,50,17,31,38,44,83,12,39,12,98,96,20,7,69,82,7,12,75,49,85,59,17,44,98,58,28,94,34,81,49,48,66,51,43,5,96,52,22,81,36,83,94,32,28,94,27,97,18,99,32,49,53,31,16,61,57,18,87,22,93,18,21,25,77,33,78,41,34,69,5,28,15,87,38,98,38,41,83,10,61,90,21,92,35,93,51,35,92,23,50,23,5,51,97,60,36,69,4,62,20,39,88,11,48,56,9,92,8,85,78,62,24,62,82,15,16,30,81,34,9,98,94,8,16,85,22,75,40,62,78,25,70,16,47,28,93,32,21,62,53,94,62,14,75,19,69,8,47,9,39,90,35,10,86,50,15,84,42,72,19,24,5,77,79,3,93,66,6,89,16,11,55,32,37,38,28,50,78,21,29,35,13,95,71,3,14,12,96,23,75,33,97,26,41,96,88,68,22,39,18,4,7,46,91,8,55,39,37,28,47,79,38,73,11,72,8,28,76,70,69,27,84,37,84,79,81,34,71,97,43,94,74,13,58,14,64,20,53,22,67,86,39,46,28,50,34,62,54,8,41,24,68,57,80,94,32,79,18,61,15,90,23,6,67,92,18,18,83,36,46,44,31,76,39,2,77,23,93,10,67,37,25,46,19,87,21,2,92,92,92,68,27,13,38,42,85,13,46,39,61,96,9,53,29,44,81,84,91,11,79,75,5,13,88,84,19,1,18,38,86,42,6,85,63,40,93,3,33,83,41,82,51,79,37,85,1,53,40,39,74,33,54,29,23,49,21,31,43,29,98,32,70,59,10,24,21,74,89,20,96,78,21,25,9,99,52,8,39,64,25,29,95,37,49,94,35,1,85,48,5,97,23,64,41,98,14,76,97,55,56,11,23,81,42,98,43,46,37,22,99,1,98,91,58,20,23,94,53,63,23,59,8,32,94,37,70,24,33,69,79,77,35,32,52,79,17,62,31,30,70,61,20,2,54,17,46,36,75,58,61,33,71,10,50,10,53,10,79,30,79,41,91,80,52,20,54,65,84,24,85,9,69,11,54,12,83,86,54,27,68,9,86,0,0,21,21,1,10,1,0,0,0,0,0,0]

steps = advent15a(advent15prog, advent15savemap, mode='auto', delay=0.000) # 270
print ("15) answer part (a):", steps)
print ("15) answer part (b):", advent15b(advent15savemap, mode='auto', delay=0.000, steps=steps)) # 364
