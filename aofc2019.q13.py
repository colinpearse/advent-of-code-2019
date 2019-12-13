# python3

# 13) run auto/manual on xterm; auto only on Jupyter

import sys
import tty
import termios
import time

# some #defines
TERM_CLEAR_SCREEN = chr(27)+'[2j'
TERM_INIT_STATE   = chr(27)+'c'
TERM_CURS_HOME    = chr(27)+'[H'
TERM_CURS_UP      = chr(27)+'[A'
TERM_CURS_DOWN    = chr(27)+'[B'
TERM_CURS_LEFT    = chr(27)+'[D'
TERM_CURS_RIGHT   = chr(27)+'[C'

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
        if x < self.__minx: self.__minx = x
        if y < self.__miny: self.__miny = y
        if x > self.__maxx: self.__maxx = x
        if y > self.__maxy: self.__maxy = y

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
    ch = sys.stdin.read(1)
    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    if   ch == 'k': return 0   # stay
    elif ch == 'j': return -1  # left
    elif ch == 'l': return 1   # right
    return 0

def getball(game):
    if len(game) < 10:
        return str(game)
    return ""

def swapdict(d):
    return dict([(v,k) for k,v in d.items()]) 

def bestmove(game):
    ballpadd = swapdict(game)
    if 3 not in ballpadd:
        return 1
    xb,yb = ballpadd[4]      # ball
    xp,yp = ballpadd[3]      # paddle
    if   xp < xb: return 1   # right
    elif xp > xb: return -1  # left
    return 0                 # stay

def advent13a(prog):
    comp = IntBox(prog)
    ret,O = comp.run([])
    game = {(O[i],O[i+1]):O[i+2] for i in range(0,len(O),3)}
    blocks = list(game.values())
    print ('blocks', blocks.count(2))
    return ret

# TERM_CURS_RIGHT default value of the matrix; the following values are mapped, see mapval:
# 0 is an empty tile
# 1 is a wall tile
# 2 is a block tile
# 3 is a horizontal paddle tile
# 4 is a ball tile
def advent13b(prog, mode='manual', delay=0.1):
    comp = IntBox(prog)
    comp.modify({0:2})
    m = VLM(defval=TERM_CURS_RIGHT)
    #fd = open("advent13.log", "w")
    score = 0
    ret = -1
    I = []
    while ret != 0:
        ret,O = comp.run(I)
        game = {(O[i],O[i+1]):O[i+2] for i in range(0,len(O),3)}

        if (-1,0) in game:
            score = game[(-1,0)]
            del game[(-1,0)]

        m.msetd(game, mapval={0:' ', 1:'|', 2:'X', 3:'-', 4:'o'})
        m.printm('join', message="JOYSTICK: j,k,l (left,stay,right)  score:%d  delay=%1.3f"%(score,delay))
        #print ("SCORE:%d BALL:%s"%(score, getball(game)), file=fd)

        if ret != 0:
            if mode == 'auto':
                I = [bestmove(game)]
            else:
                I = [getinput()]
            time.sleep(delay)
    #fd.close()
    return score

advent13prog = [1,380,379,385,1008,2399,203850,381,1005,381,12,99,109,2400,1101,0,0,383,1102,1,0,382,20101,0,382,1,21001,383,0,2,21101,37,0,0,1105,1,578,4,382,4,383,204,1,1001,382,1,382,1007,382,44,381,1005,381,22,1001,383,1,383,1007,383,20,381,1005,381,18,1006,385,69,99,104,-1,104,0,4,386,3,384,1007,384,0,381,1005,381,94,107,0,384,381,1005,381,108,1105,1,161,107,1,392,381,1006,381,161,1102,1,-1,384,1105,1,119,1007,392,42,381,1006,381,161,1102,1,1,384,20101,0,392,1,21101,18,0,2,21102,1,0,3,21101,138,0,0,1105,1,549,1,392,384,392,21001,392,0,1,21101,18,0,2,21102,1,3,3,21102,161,1,0,1105,1,549,1101,0,0,384,20001,388,390,1,21001,389,0,2,21102,1,180,0,1106,0,578,1206,1,213,1208,1,2,381,1006,381,205,20001,388,390,1,20101,0,389,2,21102,205,1,0,1105,1,393,1002,390,-1,390,1101,0,1,384,21002,388,1,1,20001,389,391,2,21101,0,228,0,1105,1,578,1206,1,261,1208,1,2,381,1006,381,253,21001,388,0,1,20001,389,391,2,21102,1,253,0,1106,0,393,1002,391,-1,391,1101,0,1,384,1005,384,161,20001,388,390,1,20001,389,391,2,21102,279,1,0,1105,1,578,1206,1,316,1208,1,2,381,1006,381,304,20001,388,390,1,20001,389,391,2,21102,1,304,0,1106,0,393,1002,390,-1,390,1002,391,-1,391,1102,1,1,384,1005,384,161,20101,0,388,1,21002,389,1,2,21101,0,0,3,21101,338,0,0,1106,0,549,1,388,390,388,1,389,391,389,21001,388,0,1,20101,0,389,2,21102,4,1,3,21101,0,365,0,1106,0,549,1007,389,19,381,1005,381,75,104,-1,104,0,104,0,99,0,1,0,0,0,0,0,0,341,20,15,1,1,22,109,3,22101,0,-2,1,22102,1,-1,2,21101,0,0,3,21102,1,414,0,1105,1,549,22102,1,-2,1,22102,1,-1,2,21102,429,1,0,1106,0,601,1202,1,1,435,1,386,0,386,104,-1,104,0,4,386,1001,387,-1,387,1005,387,451,99,109,-3,2106,0,0,109,8,22202,-7,-6,-3,22201,-3,-5,-3,21202,-4,64,-2,2207,-3,-2,381,1005,381,492,21202,-2,-1,-1,22201,-3,-1,-3,2207,-3,-2,381,1006,381,481,21202,-4,8,-2,2207,-3,-2,381,1005,381,518,21202,-2,-1,-1,22201,-3,-1,-3,2207,-3,-2,381,1006,381,507,2207,-3,-4,381,1005,381,540,21202,-4,-1,-1,22201,-3,-1,-3,2207,-3,-4,381,1006,381,529,21202,-3,1,-7,109,-8,2105,1,0,109,4,1202,-2,44,566,201,-3,566,566,101,639,566,566,1201,-1,0,0,204,-3,204,-2,204,-1,109,-4,2106,0,0,109,3,1202,-1,44,594,201,-2,594,594,101,639,594,594,20101,0,0,-2,109,-3,2106,0,0,109,3,22102,20,-2,1,22201,1,-1,1,21101,0,443,2,21102,1,526,3,21102,880,1,4,21102,1,630,0,1105,1,456,21201,1,1519,-2,109,-3,2106,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,2,2,2,2,0,0,2,2,0,2,0,0,2,2,2,2,0,2,2,2,2,0,2,0,2,0,2,0,2,0,2,0,2,0,2,0,2,0,0,2,0,1,1,0,2,0,0,2,0,2,2,2,0,2,0,2,2,2,2,2,2,0,2,2,2,2,2,2,2,0,2,0,2,0,0,0,2,2,0,0,2,2,2,2,0,1,1,0,2,2,2,2,2,2,2,2,0,2,2,2,2,2,2,0,2,2,2,2,0,0,0,2,2,0,2,2,2,2,2,2,0,0,2,2,2,2,2,2,0,1,1,0,2,0,2,2,2,2,2,0,0,2,0,0,2,0,2,2,2,2,2,2,2,0,2,0,0,2,0,2,2,2,0,2,2,2,2,2,2,2,2,2,0,1,1,0,2,2,2,0,2,0,0,2,2,0,2,2,2,0,2,0,2,2,2,2,2,0,0,0,2,0,0,2,2,2,0,2,2,0,0,0,2,2,2,0,0,1,1,0,2,2,2,2,2,2,2,0,0,2,2,2,2,0,0,2,2,2,0,2,2,2,0,2,2,2,2,0,2,0,2,2,0,2,2,2,0,2,0,2,0,1,1,0,2,2,2,2,0,2,0,2,2,2,2,2,2,2,2,0,0,0,2,2,2,0,2,0,2,0,2,2,2,2,0,2,2,0,2,0,2,0,2,0,0,1,1,0,2,2,2,2,0,2,2,0,2,2,0,0,0,2,0,2,2,2,2,0,2,0,0,0,2,2,0,2,2,2,2,0,0,2,2,2,2,0,2,2,0,1,1,0,2,2,2,0,2,2,0,2,2,2,2,2,2,2,2,2,2,2,0,2,0,0,2,2,2,2,0,2,2,2,0,2,2,2,2,2,2,0,2,2,0,1,1,0,2,2,2,2,2,0,2,2,2,0,2,2,0,0,2,2,2,0,2,2,2,2,2,2,0,2,0,2,2,0,0,2,2,0,2,2,2,0,2,2,0,1,1,0,2,2,2,2,2,0,2,2,2,0,2,2,2,2,2,0,2,0,2,2,2,0,2,0,0,2,0,2,2,2,2,2,2,2,0,2,2,2,2,2,0,1,1,0,0,2,2,2,2,2,2,0,2,2,2,2,2,2,2,0,2,0,2,2,2,2,2,2,2,2,0,2,0,0,2,2,0,2,0,2,2,2,2,2,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,11,38,49,70,10,39,91,58,63,68,52,75,23,63,39,47,35,75,29,29,52,19,47,94,19,66,22,88,37,37,78,74,50,60,79,90,76,65,62,46,70,10,5,78,40,26,89,43,42,11,26,57,77,13,3,28,60,91,71,34,83,69,11,40,97,12,59,2,35,50,62,24,93,66,1,29,31,31,70,97,37,72,39,55,83,60,6,81,2,6,49,73,44,59,88,14,13,76,25,30,85,82,12,12,20,34,11,87,11,95,16,28,84,79,10,96,48,55,62,38,1,7,65,7,63,5,30,52,48,77,31,39,87,20,70,4,91,56,48,20,90,21,89,90,27,37,20,72,89,82,93,84,30,53,85,86,16,7,1,14,2,61,75,25,57,53,89,8,36,29,22,66,21,97,55,19,65,29,55,98,40,48,84,32,87,53,98,98,63,14,29,42,63,90,30,53,58,45,31,2,16,78,84,26,86,59,68,70,42,2,45,90,62,32,62,9,68,14,27,89,97,11,96,60,6,43,29,56,2,80,52,76,92,44,66,62,13,95,7,84,81,47,7,69,33,35,33,65,7,83,15,92,49,18,31,91,40,96,44,64,56,77,31,6,16,68,13,77,32,76,29,23,92,75,32,86,45,94,88,26,79,17,29,70,14,91,9,9,71,79,1,25,72,5,16,62,3,92,8,58,30,9,11,21,7,13,26,11,65,17,83,43,94,78,10,72,96,53,53,61,53,31,73,36,12,66,65,88,81,97,54,82,60,18,81,77,46,31,68,67,55,85,63,42,43,44,71,37,31,94,63,41,61,26,9,16,78,85,54,8,62,86,91,58,42,14,85,25,62,75,55,60,1,94,84,49,67,70,96,16,97,40,5,80,83,58,24,7,42,27,33,97,97,95,94,8,44,18,64,96,80,80,14,16,27,43,26,52,32,41,6,44,83,53,89,11,50,43,64,46,9,97,21,38,59,70,89,18,98,17,69,95,44,70,35,73,22,94,4,78,11,74,15,72,87,84,85,75,34,17,65,11,96,86,39,69,55,59,56,58,97,39,54,70,71,25,15,97,29,66,78,54,54,82,92,28,28,60,98,8,18,5,30,4,3,15,65,4,89,76,27,90,36,47,75,70,82,95,44,13,63,56,36,43,92,66,61,85,73,71,60,51,56,90,44,40,73,15,76,67,51,36,44,12,58,45,17,80,97,30,57,47,96,3,95,2,27,77,84,13,69,89,78,8,45,58,22,74,84,12,10,32,16,20,4,21,98,52,55,77,24,14,38,76,82,73,39,5,19,51,75,89,31,51,60,95,89,2,15,39,17,17,77,79,60,21,21,87,81,1,95,5,5,59,3,93,3,34,51,56,11,39,29,34,56,65,36,20,16,44,28,11,44,15,59,95,30,24,33,24,64,4,6,96,62,72,40,93,30,42,45,81,49,82,77,58,9,18,60,86,53,90,57,69,26,86,67,97,90,79,77,64,19,27,13,10,89,92,33,1,23,97,72,19,11,25,89,87,65,54,93,78,34,49,36,82,61,59,76,9,97,39,32,26,54,62,62,3,33,75,29,87,6,30,92,14,23,33,58,95,92,52,12,95,70,18,64,11,81,76,47,85,40,52,51,65,91,18,30,63,59,63,66,39,76,87,63,98,65,67,17,72,63,9,73,74,12,79,35,48,17,68,40,50,13,46,75,61,53,50,26,37,44,92,46,6,42,17,85,56,85,75,90,63,73,61,74,5,18,70,39,75,67,6,16,10,36,80,28,69,37,42,39,19,40,9,4,49,8,97,82,2,44,86,86,95,49,40,26,86,71,45,11,61,9,98,82,67,88,47,54,86,89,97,6,31,59,9,81,24,76,59,95,19,40,63,9,90,83,10,45,96,80,57,16,8,97,64,36,28,37,88,64,47,19,51,92,30,15,55,2,7,73,22,2,8,82,69,39,63,48,43,27,23,40,82,57,19,42,36,92,57,66,54,8,48,94,76,70,76,203850]

print ("13) answer part (a):", advent13a(advent13prog)) # 341
print ("13) answer part (b):", advent13b(advent13prog, mode='auto', delay=0.005)) # 17138
