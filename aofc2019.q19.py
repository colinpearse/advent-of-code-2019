# python3

# 19) run on xterm

import sys
import tty
import termios

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

# TERM_CURS_RIGHT default value of the matrix; the following values are mapped, see mapval:
def advent19a(prog, delay=0.1):
    comp = IntBox(prog)
    #comp.modify({0:2})
    m = VLM(defval=TERM_CURS_RIGHT)
    gmap = {}
    res = -1
    for y in range(0,50):
        for x in range(0,50):
            I = [x,y]
            ret,O = comp.run(I)
            gmap[(x,y)] = O[0]
        m.msetd(gmap)
        m.printm(j='join', message="Q19 Olen=%d       "%(len(O)))
    return list(gmap.values()).count(1)

def advent19b(prog, delay=0.1):
    comp = IntBox(prog)
    ret = 0
    O = [0]
    y = 10
    x = 0
    while ret == 0:
        y += 1
        x -= 1
        while O[0] == 0:
            x += 1
            I = [x,y]
            ret,O = comp.run(I)

        #print ("bottom-left", I, O)
        I = [x+99,y-99]
        ret,O = comp.run(I)
        if O[0] == 1:
            print ("bottom-left", x, y)
            print ("top-right", I, O)
            print ("top-left", x, y)
            ret = x*10000 + y-99
    return ret


advent19prog = [109,424,203,1,21102,1,11,0,1105,1,282,21101,18,0,0,1106,0,259,2101,0,1,221,203,1,21102,1,31,0,1106,0,282,21101,0,38,0,1106,0,259,21002,23,1,2,22102,1,1,3,21101,0,1,1,21102,57,1,0,1106,0,303,2102,1,1,222,21002,221,1,3,21002,221,1,2,21101,0,259,1,21101,0,80,0,1105,1,225,21101,123,0,2,21101,91,0,0,1105,1,303,1201,1,0,223,20101,0,222,4,21101,259,0,3,21102,225,1,2,21101,0,225,1,21102,118,1,0,1105,1,225,21001,222,0,3,21102,58,1,2,21101,133,0,0,1105,1,303,21202,1,-1,1,22001,223,1,1,21102,1,148,0,1106,0,259,1201,1,0,223,20101,0,221,4,21002,222,1,3,21101,20,0,2,1001,132,-2,224,1002,224,2,224,1001,224,3,224,1002,132,-1,132,1,224,132,224,21001,224,1,1,21101,195,0,0,105,1,109,20207,1,223,2,20102,1,23,1,21101,-1,0,3,21102,214,1,0,1105,1,303,22101,1,1,1,204,1,99,0,0,0,0,109,5,2101,0,-4,249,22102,1,-3,1,22102,1,-2,2,22101,0,-1,3,21101,250,0,0,1105,1,225,21202,1,1,-4,109,-5,2105,1,0,109,3,22107,0,-2,-1,21202,-1,2,-1,21201,-1,-1,-1,22202,-1,-2,-2,109,-3,2106,0,0,109,3,21207,-2,0,-1,1206,-1,294,104,0,99,21201,-2,0,-2,109,-3,2106,0,0,109,5,22207,-3,-4,-1,1206,-1,346,22201,-4,-3,-4,21202,-3,-1,-1,22201,-4,-1,2,21202,2,-1,-1,22201,-4,-1,1,22102,1,-2,3,21102,1,343,0,1105,1,303,1105,1,415,22207,-2,-3,-1,1206,-1,387,22201,-3,-2,-3,21202,-2,-1,-1,22201,-3,-1,3,21202,3,-1,-1,22201,-3,-1,2,21201,-4,0,1,21102,1,384,0,1106,0,303,1105,1,415,21202,-4,-1,-4,22201,-4,-3,-4,22202,-3,-2,-2,22202,-2,-4,-4,22202,-3,-2,-3,21202,-4,-1,-2,22201,-3,-2,1,21201,1,0,-4,109,-5,2105,1,0]

beam = advent19a(advent19prog, delay=0.000) # 201
print ("17) answer part (a):", beam)
box = advent19b(advent19prog, delay=0.000)
print ("18) answer part (b):", box)  # 6610984
