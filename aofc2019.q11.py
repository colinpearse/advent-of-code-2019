# python3

# 11)

import collections
import itertools

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

def dec(n, l=4):
    return n-1 if n > 0 else l-1
def inc(n, l=4):
    return n+1 if n < l-1 else 0
def turn(face, instr):
    return dec(face) if instr == 0 else inc(face)  # 0=left 1=right
def move(pos, facing):
    x,y = pos  
    if   facing == '^': pos = (x, y+1)
    elif facing == '>': pos = (x+1, y)
    elif facing == 'v': pos = (x, y-1)
    elif facing == '<': pos = (x-1, y)
    return pos

def set_minmax(pos,minx,miny,maxx,maxy):
    x,y = pos
    return min(x,minx),min(y,miny),max(x,maxx),max(y,maxy)


def initgrid(minx,miny,maxx,maxy, black=0):
    y = maxy
    blanks = [black] * int(1 + abs(minx) + abs(maxx))
    grid = []
    while y >= miny:
        grid.append(blanks.copy())
        y -= 1
    return grid

def addroute(grid, route, minx,miny,maxx,maxy, white=0, black=1):
    rowmap = dict([(y,row) for row,y in enumerate(range(maxy,miny-1,-1))])
    colmap = dict([(x,col) for col,x in enumerate(range(minx,maxx+1,+1))])
    for pos in route:
        x,y = pos
        row,col = rowmap[y],colmap[x]
        if route[pos] == 1:
            grid[row][col] = white
    return grid

def makegrid(route, minx,miny,maxx,maxy, white=0, black=1):
    grid = initgrid(minx,miny,maxx,maxy, black=black)
    grid = addroute(grid, route, minx,miny,maxx,maxy, white=white, black=black)
    return grid

def print_grid(grid):
    for row in grid:
        print (''.join(list(map(str, row))))

# 0 is black, 1 is white
# NOTE: route doesn't have to be an ordered dict
def advent11a(prog, startI=0):
    comp = IntBox(prog)
    painted = 0
    direc = ['>','v','<','^']
    face = 3
    pos = (0,0)
    route = {pos:startI}
    minx,miny,maxx,maxy = 0,0,0,0
    ret = -1

    while ret != 0:
        I = [route[pos]]  # input: colour on pos
        ret,O = comp.run(I)

        route[pos] = O[0]            # paint
        face = turn(face, O[1])      # turn
        pos = move(pos, direc[face]) # move

        if pos not in route:
            route[pos] = 0
            minx,miny,maxx,maxy = set_minmax(pos,minx,miny,maxx,maxy)
            painted += 1

    grid = makegrid(route, minx,miny,maxx,maxy, white='o', black=' ')
    print_grid(grid)
    return painted

advent11prog = [3,8,1005,8,329,1106,0,11,0,0,0,104,1,104,0,3,8,102,-1,8,10,1001,10,1,10,4,10,1008,8,0,10,4,10,1002,8,1,29,2,1102,1,10,1,1009,16,10,2,4,4,10,1,9,5,10,3,8,1002,8,-1,10,101,1,10,10,4,10,108,0,8,10,4,10,101,0,8,66,2,106,7,10,1006,0,49,3,8,1002,8,-1,10,101,1,10,10,4,10,108,1,8,10,4,10,1002,8,1,95,1006,0,93,3,8,102,-1,8,10,1001,10,1,10,4,10,108,1,8,10,4,10,102,1,8,120,1006,0,61,2,1108,19,10,2,1003,2,10,1006,0,99,3,8,1002,8,-1,10,1001,10,1,10,4,10,1008,8,0,10,4,10,101,0,8,157,3,8,102,-1,8,10,1001,10,1,10,4,10,1008,8,1,10,4,10,1001,8,0,179,2,1108,11,10,1,1102,19,10,3,8,102,-1,8,10,1001,10,1,10,4,10,1008,8,1,10,4,10,101,0,8,209,2,108,20,10,3,8,1002,8,-1,10,101,1,10,10,4,10,108,1,8,10,4,10,101,0,8,234,3,8,102,-1,8,10,101,1,10,10,4,10,108,0,8,10,4,10,1002,8,1,256,2,1102,1,10,1006,0,69,2,108,6,10,2,4,13,10,3,8,102,-1,8,10,101,1,10,10,4,10,1008,8,0,10,4,10,1002,8,1,294,1,1107,9,10,1006,0,87,2,1006,8,10,2,1001,16,10,101,1,9,9,1007,9,997,10,1005,10,15,99,109,651,104,0,104,1,21101,387395195796,0,1,21101,346,0,0,1105,1,450,21101,0,48210129704,1,21101,0,357,0,1105,1,450,3,10,104,0,104,1,3,10,104,0,104,0,3,10,104,0,104,1,3,10,104,0,104,1,3,10,104,0,104,0,3,10,104,0,104,1,21101,0,46413147328,1,21102,404,1,0,1106,0,450,21102,179355823323,1,1,21101,415,0,0,1105,1,450,3,10,104,0,104,0,3,10,104,0,104,0,21102,1,838345843476,1,21101,0,438,0,1105,1,450,21101,709475709716,0,1,21101,449,0,0,1105,1,450,99,109,2,22102,1,-1,1,21102,40,1,2,21101,0,481,3,21101,0,471,0,1105,1,514,109,-2,2105,1,0,0,1,0,0,1,109,2,3,10,204,-1,1001,476,477,492,4,0,1001,476,1,476,108,4,476,10,1006,10,508,1101,0,0,476,109,-2,2106,0,0,0,109,4,2101,0,-1,513,1207,-3,0,10,1006,10,531,21101,0,0,-3,21201,-3,0,1,21201,-2,0,2,21101,1,0,3,21101,550,0,0,1105,1,555,109,-4,2106,0,0,109,5,1207,-3,1,10,1006,10,578,2207,-4,-2,10,1006,10,578,21201,-4,0,-4,1105,1,646,22101,0,-4,1,21201,-3,-1,2,21202,-2,2,3,21101,597,0,0,1105,1,555,22102,1,1,-4,21101,0,1,-1,2207,-4,-2,10,1006,10,616,21101,0,0,-1,22202,-2,-1,-2,2107,0,-3,10,1006,10,638,22102,1,-1,1,21101,638,0,0,106,0,513,21202,-2,-1,-2,22201,-4,-2,-4,109,-5,2106,0,0]

print ("11) answer part (a):", advent11a(advent11prog, startI=0), 'panels')  # 2594
print ()
print ("11) answer part (b):", advent11a(advent11prog, startI=1), 'panels')  # AKERJFHK
