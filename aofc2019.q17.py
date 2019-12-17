# python3

# 17) run auto/manual on xterm; auto only on Jupyter

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
        if x < self.__minx: self.__minx = x  #; self.__clearscreen = TERM_CLEAR_SEQ
        if y < self.__miny: self.__miny = y  #; self.__clearscreen = TERM_CLEAR_SEQ
        if x > self.__maxx: self.__maxx = x  #; self.__clearscreen = TERM_CLEAR_SEQ
        if y > self.__maxy: self.__maxy = y  #; self.__clearscreen = TERM_CLEAR_SEQ

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
    def run(self, I, retO=[]):
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
                lenrO = len(retO)
                if lenrO > 0 and len(O) > lenrO and retO == O[(lenrO*-1):]:
                    return 1, O  # retO equals the end of O then freeze prog for printing output
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

def is_intersection(gmap, pos):
    x,y = pos
    if (x-1,y) in gmap and gmap[(x-1,y)] == chr(35) and \
       (x+1,y) in gmap and gmap[(x+1,y)] == chr(35) and \
       (x,y-1) in gmap and gmap[(x,y-1)] == chr(35) and \
       (x,y+1) in gmap and gmap[(x,y+1)] == chr(35):
        return True
    return False

def get_intersections(gmap):
    isects = set()
    for pos in gmap:
        x,y = pos
        if gmap[pos] == chr(35) and is_intersection(gmap, pos):
            isects.add(pos)
    return isects

def calc_intersections(gmap):
    isects = get_intersections(gmap)
    return sum([(pos[0]*pos[1]) for pos in list(isects)])

def printarr(lines):
    for line in lines:
        print (line)

def joinarr(lines):
    return [''.join(line) for line in lines]

def out2arr(O, remO=[]):
    line = []
    lines = []
    for e in O:
        if e == 10:
            lines.append(''.join(line))
            line = []
        else:
            if e not in remO:
                if e <= 0 or e > 255:
                    line.append('chr('+str(e)+')')
                else:
                    line.append(chr(e))
    return lines

def out2map(gmap, pos, O):
    x,y = pos
    for e in O:
        if e == 10:
            if x == 0:
                y = 0
            else:
                y += 1
            x = 0
        else:
            if e <= 0 or e > 255:
                gmap[pos] = e
            else:
                gmap[pos] = chr(e)
            x += 1
        pos = (x,y)
    return gmap, pos

def swapdict(d):
    return dict([(v,k) for k,v in d.items()]) 

def getres(gmap):
    a = [e for e in gmap.values() if isinstance(e,int)]
    if a:
        return max(a)
    return -1

def getinput():
    inp = input()
    moves = []
    for i in list(inp):
        moves.append(ord(i))
    return moves

# TERM_CURS_RIGHT default value of the matrix; the following values are mapped, see mapval:
# Input: ?
# Output:
# 46 means .
# 35 means # (scaffold)
# 10 newline
def advent17a(prog, mode='manual', delay=0.1):
    comp = IntBox(prog)
    pos = (0,0)
    gmap = {}
    I = []
    for i in range(1):
        time.sleep(delay)
        ret,O = comp.run(I)
        gmap, pos = out2map(gmap, pos, O)
        printarr(out2arr(O))
    return calc_intersections(gmap)


# TERM_CURS_RIGHT default value of the matrix; the following values are mapped, see mapval:
# Input: ?
# Output:
# 46 means .
# 35 means # (scaffold)
# 10 newline
def advent17b(prog, SEQ, A, B, C, FEED, mode='manual', delay=0.1, isects=-1):
    comp = IntBox(prog)
    comp.modify({0:2})
    m = VLM(defval=TERM_CURS_RIGHT)
    #fdlog = open("advent17.log", "w")
    pos = (0,0)
    gmap = {}
    res = -1
    i = 0
    inputs = ["",SEQ,A,B,C,FEED]
    while res == -1:
        if i < len(inputs):
            I = [ord(i) for i in list(inputs[i])] + [10]
            i += 1
        else:
            I = []
        #I = getinput() + [10]
        #print ("INPUT", joinarr(out2arr(I)), file=fdlog)

        ret,O = comp.run(I, retO=[10,10])
        #print ("OUTPUT", joinarr(out2arr(O, remO=[46,35])), file=fdlog)

        gmap, pos = out2map(gmap, pos, O)
        if res == -1:
            res = getres(gmap)
        m.msetd(gmap)
        m.printm(j='join', message="Q17 (a)=%d (b)=%d    delay=%1.3f  Olen=%d       "%(isects, res, delay, len(O)))
        time.sleep(delay)
    #fdlog.close()
    return res


advent17prog = [1,330,331,332,109,4718,1101,0,1182,16,1101,1469,0,24,101,0,0,570,1006,570,36,101,0,571,0,1001,570,-1,570,1001,24,1,24,1106,0,18,1008,571,0,571,1001,16,1,16,1008,16,1469,570,1006,570,14,21102,58,1,0,1106,0,786,1006,332,62,99,21101,333,0,1,21101,0,73,0,1105,1,579,1102,1,0,572,1101,0,0,573,3,574,101,1,573,573,1007,574,65,570,1005,570,151,107,67,574,570,1005,570,151,1001,574,-64,574,1002,574,-1,574,1001,572,1,572,1007,572,11,570,1006,570,165,101,1182,572,127,101,0,574,0,3,574,101,1,573,573,1008,574,10,570,1005,570,189,1008,574,44,570,1006,570,158,1105,1,81,21101,0,340,1,1106,0,177,21102,477,1,1,1105,1,177,21101,0,514,1,21102,176,1,0,1105,1,579,99,21102,184,1,0,1106,0,579,4,574,104,10,99,1007,573,22,570,1006,570,165,1001,572,0,1182,21102,375,1,1,21102,211,1,0,1106,0,579,21101,1182,11,1,21101,222,0,0,1106,0,979,21102,388,1,1,21101,233,0,0,1105,1,579,21101,1182,22,1,21101,244,0,0,1106,0,979,21101,0,401,1,21101,255,0,0,1106,0,579,21101,1182,33,1,21102,1,266,0,1105,1,979,21101,0,414,1,21101,0,277,0,1105,1,579,3,575,1008,575,89,570,1008,575,121,575,1,575,570,575,3,574,1008,574,10,570,1006,570,291,104,10,21102,1,1182,1,21101,313,0,0,1106,0,622,1005,575,327,1101,1,0,575,21101,0,327,0,1105,1,786,4,438,99,0,1,1,6,77,97,105,110,58,10,33,10,69,120,112,101,99,116,101,100,32,102,117,110,99,116,105,111,110,32,110,97,109,101,32,98,117,116,32,103,111,116,58,32,0,12,70,117,110,99,116,105,111,110,32,65,58,10,12,70,117,110,99,116,105,111,110,32,66,58,10,12,70,117,110,99,116,105,111,110,32,67,58,10,23,67,111,110,116,105,110,117,111,117,115,32,118,105,100,101,111,32,102,101,101,100,63,10,0,37,10,69,120,112,101,99,116,101,100,32,82,44,32,76,44,32,111,114,32,100,105,115,116,97,110,99,101,32,98,117,116,32,103,111,116,58,32,36,10,69,120,112,101,99,116,101,100,32,99,111,109,109,97,32,111,114,32,110,101,119,108,105,110,101,32,98,117,116,32,103,111,116,58,32,43,10,68,101,102,105,110,105,116,105,111,110,115,32,109,97,121,32,98,101,32,97,116,32,109,111,115,116,32,50,48,32,99,104,97,114,97,99,116,101,114,115,33,10,94,62,118,60,0,1,0,-1,-1,0,1,0,0,0,0,0,0,1,28,8,0,109,4,2102,1,-3,586,21002,0,1,-1,22101,1,-3,-3,21101,0,0,-2,2208,-2,-1,570,1005,570,617,2201,-3,-2,609,4,0,21201,-2,1,-2,1105,1,597,109,-4,2105,1,0,109,5,1201,-4,0,630,20101,0,0,-2,22101,1,-4,-4,21101,0,0,-3,2208,-3,-2,570,1005,570,781,2201,-4,-3,653,20101,0,0,-1,1208,-1,-4,570,1005,570,709,1208,-1,-5,570,1005,570,734,1207,-1,0,570,1005,570,759,1206,-1,774,1001,578,562,684,1,0,576,576,1001,578,566,692,1,0,577,577,21101,702,0,0,1105,1,786,21201,-1,-1,-1,1106,0,676,1001,578,1,578,1008,578,4,570,1006,570,724,1001,578,-4,578,21102,1,731,0,1106,0,786,1105,1,774,1001,578,-1,578,1008,578,-1,570,1006,570,749,1001,578,4,578,21101,756,0,0,1105,1,786,1106,0,774,21202,-1,-11,1,22101,1182,1,1,21102,1,774,0,1105,1,622,21201,-3,1,-3,1105,1,640,109,-5,2106,0,0,109,7,1005,575,802,20101,0,576,-6,20102,1,577,-5,1106,0,814,21102,0,1,-1,21101,0,0,-5,21101,0,0,-6,20208,-6,576,-2,208,-5,577,570,22002,570,-2,-2,21202,-5,57,-3,22201,-6,-3,-3,22101,1469,-3,-3,1201,-3,0,843,1005,0,863,21202,-2,42,-4,22101,46,-4,-4,1206,-2,924,21101,0,1,-1,1106,0,924,1205,-2,873,21101,0,35,-4,1105,1,924,1202,-3,1,878,1008,0,1,570,1006,570,916,1001,374,1,374,2101,0,-3,895,1101,2,0,0,1201,-3,0,902,1001,438,0,438,2202,-6,-5,570,1,570,374,570,1,570,438,438,1001,578,558,921,21001,0,0,-4,1006,575,959,204,-4,22101,1,-6,-6,1208,-6,57,570,1006,570,814,104,10,22101,1,-5,-5,1208,-5,57,570,1006,570,810,104,10,1206,-1,974,99,1206,-1,974,1101,0,1,575,21101,973,0,0,1106,0,786,99,109,-7,2106,0,0,109,6,21102,0,1,-4,21101,0,0,-3,203,-2,22101,1,-3,-3,21208,-2,82,-1,1205,-1,1030,21208,-2,76,-1,1205,-1,1037,21207,-2,48,-1,1205,-1,1124,22107,57,-2,-1,1205,-1,1124,21201,-2,-48,-2,1105,1,1041,21102,1,-4,-2,1106,0,1041,21102,-5,1,-2,21201,-4,1,-4,21207,-4,11,-1,1206,-1,1138,2201,-5,-4,1059,1201,-2,0,0,203,-2,22101,1,-3,-3,21207,-2,48,-1,1205,-1,1107,22107,57,-2,-1,1205,-1,1107,21201,-2,-48,-2,2201,-5,-4,1090,20102,10,0,-1,22201,-2,-1,-2,2201,-5,-4,1103,2101,0,-2,0,1105,1,1060,21208,-2,10,-1,1205,-1,1162,21208,-2,44,-1,1206,-1,1131,1105,1,989,21102,1,439,1,1105,1,1150,21101,477,0,1,1106,0,1150,21102,1,514,1,21102,1,1149,0,1106,0,579,99,21102,1,1157,0,1106,0,579,204,-2,104,10,99,21207,-3,22,-1,1206,-1,1138,1201,-5,0,1176,2102,1,-4,0,109,-6,2106,0,0,18,7,50,1,5,1,50,1,5,1,50,1,5,1,50,1,5,1,50,1,5,1,50,1,5,1,50,1,5,1,50,11,19,9,24,1,23,1,7,1,24,13,11,1,7,1,36,1,11,1,7,1,36,1,11,1,7,1,36,1,11,1,7,1,36,1,9,11,36,1,9,1,1,1,44,1,9,1,1,1,44,1,9,1,1,1,44,13,54,1,56,1,56,1,56,1,56,1,56,1,56,1,48,9,48,1,56,1,56,1,56,1,56,1,56,1,56,1,28,9,19,1,28,1,7,1,19,1,28,1,7,1,19,1,28,1,7,1,19,1,28,1,7,1,19,11,18,1,7,1,29,1,16,13,1,1,25,1,16,1,1,1,7,1,1,1,1,1,25,1,16,1,1,1,7,11,19,1,16,1,1,1,9,1,1,1,5,1,19,1,8,11,9,1,1,1,5,1,19,1,8,1,7,1,11,1,1,1,5,1,19,1,8,1,7,1,11,1,1,1,5,1,11,9,8,1,7,1,11,1,1,1,5,1,11,1,16,1,7,1,11,13,7,1,16,1,7,1,13,1,5,1,3,1,7,1,16,9,13,7,3,1,7,1,48,1,7,1,48,1,7,1,48,1,7,1,48,1,7,1,48,1,7,1,48,9,16]

# hardcoded moves for (b)
moves = "L,10,R,8,R,6,R,10,L,12,R,8,L,12,L,10,R,8,R,6,R,10,L,12,R,8,L,12,L,10,R,8,R,8,L,10,R,8,R,8,L,12,R,8,L,12,L,10,R,8,R,6,R,10,L,10,R,8,R,8,L,10,R,8,R,6,R,10"
movesLnum = "L10,R8,R6,R10,L12,R8,L12,L10,R8,R6,R10,L12,R8,L12,L10,R8,R8,L10,R8,R8,L12,R8,L12,L10,R8,R6,R10,L10,R8,R8,L10,R8,R6,R10"
A = "L,10,R,8,R,6,R,10"
B = "L,12,R,8,L,12"
C = "L,10,R,8,R,8"
SEQ = "A,B,A,B,C,C,B,A,C,A"
FEED = 'n'

isects = advent17a(advent17prog, mode='auto', delay=0.000) # 7328
dust = advent17b(advent17prog, SEQ, A, B, C, FEED, mode='auto', delay=0.005, isects=isects) # 1289413
print ("17) answer part (a):", isects)
print ("17) answer part (b):", dust)
print ()
print ("change FEED to 'y' to see robot move")
