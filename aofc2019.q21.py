# python3

# 21) run auto/manual on xterm; auto only on Jupyter

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
        for y in range(0, miny, incy):
            sys.stdout.write(TERM_CURS_DOWN)
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
        if val == self.__defval:
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
    miny = y
    for e in O:
        if e == 10:
            if x == 0:  # is it two newlines (redraw)?
                y = miny
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

# TERM_CURS_RIGHT default value of the matrix; the following values are mapped, see mapval:
def advent21a(prog, rprog, delay=0.2):
    comp = IntBox(prog)
    m = VLM(defval=TERM_CURS_RIGHT)
    pos = (0,0)
    gmap = {}
    fdlog = open("advent21.log", "w")

    I = list(map(lambda c:ord(c), list(rprog)))
    print ("INPUT", joinarr(out2arr(I)), file=fdlog)
    ret,O = comp.run(I)
    print ("OUTPUT", joinarr(out2arr(O)), file=fdlog)
    printarr(out2arr(O))

    ret = -1
    while ret != 0:
        ret,O = comp.run(I, retO=[10,10])
        print ("OUTPUT", joinarr(out2arr(O)), file=fdlog)
        I = []
        gmap, pos = out2map(gmap, pos, O)
        m.msetd(gmap)
        m.printm(j='join', message="Q21  delay=%1.3f  ret=%d  Olen=%d       "%(delay, ret, len(O)))
        time.sleep(delay)
    fdlog.close()
    return gmap[(0,0)] if isinstance(gmap[(0,0)],int) else 0

def advent21b(prog, rprog, delay=0.2):
    return advent21a(prog, rprog, delay=delay)

advent21prog = [109,2050,21102,1,966,1,21102,1,13,0,1106,0,1378,21101,0,20,0,1106,0,1337,21101,0,27,0,1106,0,1279,1208,1,65,748,1005,748,73,1208,1,79,748,1005,748,110,1208,1,78,748,1005,748,132,1208,1,87,748,1005,748,169,1208,1,82,748,1005,748,239,21101,0,1041,1,21102,1,73,0,1106,0,1421,21102,78,1,1,21101,0,1041,2,21102,1,88,0,1106,0,1301,21101,0,68,1,21101,1041,0,2,21101,103,0,0,1106,0,1301,1102,1,1,750,1105,1,298,21102,1,82,1,21102,1041,1,2,21101,0,125,0,1105,1,1301,1102,1,2,750,1105,1,298,21102,79,1,1,21102,1041,1,2,21101,147,0,0,1106,0,1301,21101,84,0,1,21101,0,1041,2,21102,162,1,0,1106,0,1301,1102,1,3,750,1105,1,298,21102,65,1,1,21102,1041,1,2,21101,184,0,0,1105,1,1301,21102,1,76,1,21101,1041,0,2,21102,199,1,0,1106,0,1301,21102,1,75,1,21101,0,1041,2,21101,0,214,0,1105,1,1301,21102,1,221,0,1105,1,1337,21101,10,0,1,21101,0,1041,2,21101,0,236,0,1106,0,1301,1106,0,553,21101,0,85,1,21101,1041,0,2,21102,1,254,0,1106,0,1301,21102,78,1,1,21102,1,1041,2,21101,0,269,0,1105,1,1301,21102,276,1,0,1106,0,1337,21102,10,1,1,21102,1,1041,2,21102,291,1,0,1106,0,1301,1101,1,0,755,1106,0,553,21101,32,0,1,21101,0,1041,2,21102,1,313,0,1105,1,1301,21101,0,320,0,1105,1,1337,21101,327,0,0,1106,0,1279,1202,1,1,749,21102,65,1,2,21102,73,1,3,21102,346,1,0,1105,1,1889,1206,1,367,1007,749,69,748,1005,748,360,1101,0,1,756,1001,749,-64,751,1105,1,406,1008,749,74,748,1006,748,381,1101,-1,0,751,1106,0,406,1008,749,84,748,1006,748,395,1102,1,-2,751,1105,1,406,21101,0,1100,1,21102,1,406,0,1105,1,1421,21102,1,32,1,21102,1100,1,2,21101,421,0,0,1106,0,1301,21101,428,0,0,1106,0,1337,21102,435,1,0,1106,0,1279,1202,1,1,749,1008,749,74,748,1006,748,453,1101,0,-1,752,1105,1,478,1008,749,84,748,1006,748,467,1102,1,-2,752,1106,0,478,21101,0,1168,1,21101,478,0,0,1106,0,1421,21101,0,485,0,1106,0,1337,21102,10,1,1,21102,1,1168,2,21102,500,1,0,1105,1,1301,1007,920,15,748,1005,748,518,21102,1,1209,1,21101,518,0,0,1105,1,1421,1002,920,3,529,1001,529,921,529,101,0,750,0,1001,529,1,537,102,1,751,0,1001,537,1,545,1002,752,1,0,1001,920,1,920,1105,1,13,1005,755,577,1006,756,570,21102,1100,1,1,21102,1,570,0,1106,0,1421,21101,0,987,1,1105,1,581,21101,0,1001,1,21101,588,0,0,1106,0,1378,1101,758,0,593,1001,0,0,753,1006,753,654,20101,0,753,1,21101,610,0,0,1106,0,667,21102,1,0,1,21101,621,0,0,1105,1,1463,1205,1,647,21102,1015,1,1,21101,0,635,0,1106,0,1378,21102,1,1,1,21102,1,646,0,1105,1,1463,99,1001,593,1,593,1106,0,592,1006,755,664,1102,0,1,755,1106,0,647,4,754,99,109,2,1101,0,726,757,22101,0,-1,1,21102,9,1,2,21101,697,0,3,21101,0,692,0,1106,0,1913,109,-2,2106,0,0,109,2,101,0,757,706,1201,-1,0,0,1001,757,1,757,109,-2,2106,0,0,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,255,63,191,223,127,159,95,0,170,122,102,166,184,142,77,113,215,202,162,219,154,231,92,123,197,247,85,87,138,181,174,55,185,153,234,107,254,124,249,84,139,233,213,226,115,246,228,99,34,121,118,163,137,54,169,57,106,46,38,125,189,119,51,103,175,79,157,61,207,221,71,251,238,178,86,78,232,47,187,203,253,248,136,94,69,201,190,205,117,227,156,98,177,42,100,204,114,200,188,76,35,49,252,236,196,206,70,143,182,62,198,168,229,68,93,230,60,183,243,199,237,43,140,244,155,222,126,241,216,214,58,218,217,50,239,141,56,158,171,109,235,245,179,152,101,59,116,108,212,250,120,111,173,172,39,242,220,167,186,53,110,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,20,73,110,112,117,116,32,105,110,115,116,114,117,99,116,105,111,110,115,58,10,13,10,87,97,108,107,105,110,103,46,46,46,10,10,13,10,82,117,110,110,105,110,103,46,46,46,10,10,25,10,68,105,100,110,39,116,32,109,97,107,101,32,105,116,32,97,99,114,111,115,115,58,10,10,58,73,110,118,97,108,105,100,32,111,112,101,114,97,116,105,111,110,59,32,101,120,112,101,99,116,101,100,32,115,111,109,101,116,104,105,110,103,32,108,105,107,101,32,65,78,68,44,32,79,82,44,32,111,114,32,78,79,84,67,73,110,118,97,108,105,100,32,102,105,114,115,116,32,97,114,103,117,109,101,110,116,59,32,101,120,112,101,99,116,101,100,32,115,111,109,101,116,104,105,110,103,32,108,105,107,101,32,65,44,32,66,44,32,67,44,32,68,44,32,74,44,32,111,114,32,84,40,73,110,118,97,108,105,100,32,115,101,99,111,110,100,32,97,114,103,117,109,101,110,116,59,32,101,120,112,101,99,116,101,100,32,74,32,111,114,32,84,52,79,117,116,32,111,102,32,109,101,109,111,114,121,59,32,97,116,32,109,111,115,116,32,49,53,32,105,110,115,116,114,117,99,116,105,111,110,115,32,99,97,110,32,98,101,32,115,116,111,114,101,100,0,109,1,1005,1262,1270,3,1262,20102,1,1262,0,109,-1,2105,1,0,109,1,21102,1288,1,0,1106,0,1263,20102,1,1262,0,1101,0,0,1262,109,-1,2106,0,0,109,5,21101,0,1310,0,1106,0,1279,22102,1,1,-2,22208,-2,-4,-1,1205,-1,1332,21202,-3,1,1,21101,0,1332,0,1106,0,1421,109,-5,2105,1,0,109,2,21101,1346,0,0,1105,1,1263,21208,1,32,-1,1205,-1,1363,21208,1,9,-1,1205,-1,1363,1105,1,1373,21102,1370,1,0,1105,1,1279,1105,1,1339,109,-2,2105,1,0,109,5,1202,-4,1,1385,21002,0,1,-2,22101,1,-4,-4,21102,0,1,-3,22208,-3,-2,-1,1205,-1,1416,2201,-4,-3,1408,4,0,21201,-3,1,-3,1105,1,1396,109,-5,2105,1,0,109,2,104,10,21202,-1,1,1,21102,1436,1,0,1106,0,1378,104,10,99,109,-2,2105,1,0,109,3,20002,593,753,-1,22202,-1,-2,-1,201,-1,754,754,109,-3,2106,0,0,109,10,21101,0,5,-5,21102,1,1,-4,21101,0,0,-3,1206,-9,1555,21101,3,0,-6,21102,1,5,-7,22208,-7,-5,-8,1206,-8,1507,22208,-6,-4,-8,1206,-8,1507,104,64,1106,0,1529,1205,-6,1527,1201,-7,716,1515,21002,0,-11,-8,21201,-8,46,-8,204,-8,1105,1,1529,104,46,21201,-7,1,-7,21207,-7,22,-8,1205,-8,1488,104,10,21201,-6,-1,-6,21207,-6,0,-8,1206,-8,1484,104,10,21207,-4,1,-8,1206,-8,1569,21101,0,0,-9,1105,1,1689,21208,-5,21,-8,1206,-8,1583,21101,1,0,-9,1105,1,1689,1201,-5,716,1588,21001,0,0,-2,21208,-4,1,-1,22202,-2,-1,-1,1205,-2,1613,22102,1,-5,1,21101,0,1613,0,1105,1,1444,1206,-1,1634,21202,-5,1,1,21102,1,1627,0,1106,0,1694,1206,1,1634,21102,2,1,-3,22107,1,-4,-8,22201,-1,-8,-8,1206,-8,1649,21201,-5,1,-5,1206,-3,1663,21201,-3,-1,-3,21201,-4,1,-4,1105,1,1667,21201,-4,-1,-4,21208,-4,0,-1,1201,-5,716,1676,22002,0,-1,-1,1206,-1,1686,21101,0,1,-4,1105,1,1477,109,-10,2106,0,0,109,11,21101,0,0,-6,21101,0,0,-8,21102,0,1,-7,20208,-6,920,-9,1205,-9,1880,21202,-6,3,-9,1201,-9,921,1724,21002,0,1,-5,1001,1724,1,1733,20101,0,0,-4,22101,0,-4,1,21101,0,1,2,21102,1,9,3,21102,1754,1,0,1105,1,1889,1206,1,1772,2201,-10,-4,1766,1001,1766,716,1766,21001,0,0,-3,1106,0,1790,21208,-4,-1,-9,1206,-9,1786,22101,0,-8,-3,1105,1,1790,21202,-7,1,-3,1001,1733,1,1796,20102,1,0,-2,21208,-2,-1,-9,1206,-9,1812,22102,1,-8,-1,1106,0,1816,22102,1,-7,-1,21208,-5,1,-9,1205,-9,1837,21208,-5,2,-9,1205,-9,1844,21208,-3,0,-1,1106,0,1855,22202,-3,-1,-1,1106,0,1855,22201,-3,-1,-1,22107,0,-1,-1,1105,1,1855,21208,-2,-1,-9,1206,-9,1869,22102,1,-1,-8,1105,1,1873,21201,-1,0,-7,21201,-6,1,-6,1105,1,1708,22101,0,-8,-10,109,-11,2106,0,0,109,7,22207,-6,-5,-3,22207,-4,-6,-2,22201,-3,-2,-1,21208,-1,0,-6,109,-7,2106,0,0,0,109,5,1202,-2,1,1912,21207,-4,0,-1,1206,-1,1930,21101,0,0,-4,21201,-4,0,1,22102,1,-3,2,21102,1,1,3,21102,1,1949,0,1106,0,1954,109,-5,2106,0,0,109,6,21207,-4,1,-1,1206,-1,1977,22207,-5,-3,-1,1206,-1,1977,22102,1,-5,-5,1106,0,2045,21201,-5,0,1,21201,-4,-1,2,21202,-3,2,3,21102,1,1996,0,1106,0,1954,21201,1,0,-5,21101,0,1,-2,22207,-5,-3,-1,1206,-1,2015,21102,0,1,-2,22202,-3,-2,-3,22107,0,-4,-1,1206,-1,2037,21202,-2,1,1,21101,0,2037,0,105,1,1912,21202,-3,-1,-3,22201,-5,-3,-5,109,-6,2105,1,0]

rprog21a='''NOT T T
AND A T
AND B T
AND C T
NOT T T
OR D J
AND T J
WALK
'''

rprog21b='''NOT T T
AND A T
AND B T
AND C T
NOT T T
OR D J
AND T J
RUN
'''

print ("21) answer part (a):", advent21a(advent21prog, rprog21a))   # 19353619
print ("21) answer part (b):", advent21b(advent21prog, rprog21b))   # 
