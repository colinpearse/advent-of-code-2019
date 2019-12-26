# python3

# 23) run auto/manual on xterm; auto only on Jupyter

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
def advent23a(prog, delay=0.2):
    comp = [IntBox(prog) for addr in range(50)]
    Inet = [[[addr]]     for addr in range(50)]
    Onet = [[]           for addr in range(50)]
    ret = 1
    while ret == 1:
        for addr in range(50):
            if Inet[addr]:
                I = Inet[addr].pop(0) # I = [addr] or [X,Y]
            else:
                I = [-1]              # I = [-1]  (no packet to be received)
            ret,O = comp[addr].run(I) # O = [addr, X Y, ...]
            Onet[addr] = O

        for addr in range(50):
            i = 0
            while i < len(Onet[addr]):
                daddr = Onet[addr][i]
                X     = Onet[addr][i+1]
                Y     = Onet[addr][i+2]
                if daddr == 255:
                    ret = Y
                    break
                else:
                    Inet[daddr] += [[X,Y]]
                i += 3
            Onet[addr] = []
    return ret

# TERM_CURS_RIGHT default value of the matrix; the following values are mapped, see mapval:
def advent23b(prog, delay=0.2):
    comp = [IntBox(prog) for addr in range(50)]
    Inet = [[[addr]]     for addr in range(50)]
    idle = [0            for addr in range(50)]
    Onet = [[]           for addr in range(50)]
    NAT  = []  # Not Always Transmitting
    NATh = []
    NATo = []
    #fdlog = sys.stdout
    #fdlog = open("advent23.log", "w")
    fdlog = open("/dev/null", "w")
    ret = 1
    while ret == 1:
        if set(idle) == set([1]) and NAT:
            print ("---ALL IDLE--- sending %s to addr=0"%(str(NAT)), file=fdlog)
            Inet[0] += [NAT]
            if NATo and NATo == NAT:
                ret = [NAT[1]]
                break
            else:
                NATo = NAT

        if fdlog == sys.stdout:
            print ("press return")
            input()

        for addr in range(50):
            if Inet[addr]:
                I = Inet[addr].pop(0) # I = [addr] or [X,Y]
                idle[addr] = 0
            else:
                I = [-1]              # I = [-1]  (no packet to be received)
                idle[addr] = 1
            if I[0] != -1: print ("%02d: INPUT: %s"%(addr, str(I)), file=fdlog)

            ret,O = comp[addr].run(I) # O = [addr, X Y, ...]
            if O: print ("%02d: OUTPUT: %s"%(addr, str(O)), file=fdlog)
            else: print ("%02d: OUTPUT: <no output>"%(addr), file=fdlog)
            Onet[addr] = O

        for addr in range(50):
            i = 0
            while i < len(Onet[addr]):
                daddr = Onet[addr][i]
                X     = Onet[addr][i+1]
                Y     = Onet[addr][i+2]
                if daddr == 255:
                    NAT = [X,Y]
                    NATh += [Y]
                    print ("%02d: NAT: %s"%(addr, str(NAT)), file=fdlog)
                else:
                    Inet[daddr] += [[X,Y]]
                i += 3
            Onet[addr] = []

    if fdlog != sys.stdout:
        fdlog.close()
    print ("NAT history:", NATh)
    return ret

advent23prog = [3,62,1001,62,11,10,109,2245,105,1,0,1553,1769,666,1866,1699,2216,606,1139,1965,2084,1629,790,1104,1046,1440,1660,1594,1730,1075,571,1831,1802,951,1339,1178,920,2185,1207,2154,2006,637,2045,695,1479,1930,1899,1516,982,1240,1269,852,730,2123,883,1409,1378,1017,821,1308,761,0,0,0,0,0,0,0,0,0,0,0,0,3,64,1008,64,-1,62,1006,62,88,1006,61,170,1106,0,73,3,65,20101,0,64,1,20102,1,66,2,21101,0,105,0,1105,1,436,1201,1,-1,64,1007,64,0,62,1005,62,73,7,64,67,62,1006,62,73,1002,64,2,132,1,132,68,132,1002,0,1,62,1001,132,1,140,8,0,65,63,2,63,62,62,1005,62,73,1002,64,2,161,1,161,68,161,1102,1,1,0,1001,161,1,169,102,1,65,0,1102,1,1,61,1102,1,0,63,7,63,67,62,1006,62,203,1002,63,2,194,1,68,194,194,1006,0,73,1001,63,1,63,1106,0,178,21101,0,210,0,105,1,69,1202,1,1,70,1101,0,0,63,7,63,71,62,1006,62,250,1002,63,2,234,1,72,234,234,4,0,101,1,234,240,4,0,4,70,1001,63,1,63,1106,0,218,1106,0,73,109,4,21101,0,0,-3,21101,0,0,-2,20207,-2,67,-1,1206,-1,293,1202,-2,2,283,101,1,283,283,1,68,283,283,22001,0,-3,-3,21201,-2,1,-2,1105,1,263,21201,-3,0,-3,109,-4,2106,0,0,109,4,21101,1,0,-3,21101,0,0,-2,20207,-2,67,-1,1206,-1,342,1202,-2,2,332,101,1,332,332,1,68,332,332,22002,0,-3,-3,21201,-2,1,-2,1105,1,312,21201,-3,0,-3,109,-4,2105,1,0,109,1,101,1,68,359,20102,1,0,1,101,3,68,366,21002,0,1,2,21101,0,376,0,1106,0,436,22101,0,1,0,109,-1,2106,0,0,1,2,4,8,16,32,64,128,256,512,1024,2048,4096,8192,16384,32768,65536,131072,262144,524288,1048576,2097152,4194304,8388608,16777216,33554432,67108864,134217728,268435456,536870912,1073741824,2147483648,4294967296,8589934592,17179869184,34359738368,68719476736,137438953472,274877906944,549755813888,1099511627776,2199023255552,4398046511104,8796093022208,17592186044416,35184372088832,70368744177664,140737488355328,281474976710656,562949953421312,1125899906842624,109,8,21202,-6,10,-5,22207,-7,-5,-5,1205,-5,521,21101,0,0,-4,21101,0,0,-3,21102,51,1,-2,21201,-2,-1,-2,1201,-2,385,471,20101,0,0,-1,21202,-3,2,-3,22207,-7,-1,-5,1205,-5,496,21201,-3,1,-3,22102,-1,-1,-5,22201,-7,-5,-7,22207,-3,-6,-5,1205,-5,515,22102,-1,-6,-5,22201,-3,-5,-3,22201,-1,-4,-4,1205,-2,461,1105,1,547,21102,1,-1,-4,21202,-6,-1,-6,21207,-7,0,-5,1205,-5,547,22201,-7,-6,-7,21201,-4,1,-4,1106,0,529,22101,0,-4,-7,109,-8,2105,1,0,109,1,101,1,68,564,20102,1,0,0,109,-1,2106,0,0,1102,3673,1,66,1101,0,3,67,1101,0,598,68,1101,302,0,69,1101,0,1,71,1102,604,1,72,1106,0,73,0,0,0,0,0,0,29,96377,1101,0,99377,66,1101,1,0,67,1102,633,1,68,1102,1,556,69,1101,0,1,71,1101,635,0,72,1106,0,73,1,-195,7,179734,1101,41593,0,66,1102,1,1,67,1102,1,664,68,1101,0,556,69,1102,1,0,71,1102,666,1,72,1106,0,73,1,1977,1102,1,15683,66,1102,1,1,67,1102,1,693,68,1102,556,1,69,1102,0,1,71,1101,0,695,72,1106,0,73,1,1403,1101,2287,0,66,1101,0,1,67,1101,0,722,68,1102,556,1,69,1101,3,0,71,1102,1,724,72,1106,0,73,1,10,14,282265,33,291908,8,156316,1101,68483,0,66,1102,1,1,67,1102,757,1,68,1101,0,556,69,1102,1,1,71,1102,759,1,72,1105,1,73,1,-263,16,104089,1102,1,89083,66,1102,1,1,67,1102,788,1,68,1102,556,1,69,1101,0,0,71,1102,1,790,72,1105,1,73,1,1500,1102,1,74383,66,1102,1,1,67,1102,817,1,68,1102,556,1,69,1101,1,0,71,1102,1,819,72,1106,0,73,1,673,19,7346,1102,1,19457,66,1102,1,1,67,1102,1,848,68,1102,556,1,69,1101,1,0,71,1101,850,0,72,1105,1,73,1,30,1,23957,1102,54679,1,66,1101,1,0,67,1101,879,0,68,1102,1,556,69,1102,1,1,71,1101,881,0,72,1105,1,73,1,361,19,11019,1101,34673,0,66,1101,0,4,67,1102,910,1,68,1102,302,1,69,1101,1,0,71,1101,0,918,72,1105,1,73,0,0,0,0,0,0,0,0,29,192754,1102,9397,1,66,1101,0,1,67,1101,0,947,68,1102,1,556,69,1101,1,0,71,1101,0,949,72,1106,0,73,1,89,43,34673,1102,1,11273,66,1102,1,1,67,1101,978,0,68,1101,556,0,69,1102,1,1,71,1102,1,980,72,1105,1,73,1,353,37,270813,1102,90271,1,66,1101,0,3,67,1102,1009,1,68,1101,0,302,69,1101,0,1,71,1101,1015,0,72,1105,1,73,0,0,0,0,0,0,14,225812,1101,0,82567,66,1102,1,1,67,1102,1044,1,68,1101,556,0,69,1101,0,0,71,1102,1,1046,72,1106,0,73,1,1385,1102,102253,1,66,1101,1,0,67,1101,0,1073,68,1102,1,556,69,1101,0,0,71,1101,1075,0,72,1105,1,73,1,1870,1101,5651,0,66,1101,0,1,67,1102,1102,1,68,1102,556,1,69,1102,1,0,71,1101,0,1104,72,1106,0,73,1,1802,1102,56093,1,66,1101,0,1,67,1101,0,1131,68,1102,556,1,69,1102,1,3,71,1102,1133,1,72,1105,1,73,1,13,9,92383,31,211467,7,449335,1101,0,89867,66,1102,1,5,67,1102,1,1166,68,1102,1,302,69,1102,1,1,71,1101,0,1176,72,1106,0,73,0,0,0,0,0,0,0,0,0,0,20,272661,1101,26881,0,66,1101,0,1,67,1101,0,1205,68,1102,1,556,69,1101,0,0,71,1102,1207,1,72,1105,1,73,1,1015,1102,1,1489,66,1101,0,2,67,1102,1,1234,68,1102,1,302,69,1101,0,1,71,1101,0,1238,72,1106,0,73,0,0,0,0,36,220244,1101,13567,0,66,1102,1,1,67,1102,1267,1,68,1101,556,0,69,1101,0,0,71,1102,1269,1,72,1105,1,73,1,1451,1102,57089,1,66,1102,1,1,67,1102,1296,1,68,1101,0,556,69,1102,5,1,71,1102,1,1298,72,1106,0,73,1,2,9,184766,31,70489,7,359468,8,39079,8,195395,1101,6661,0,66,1102,1,1,67,1102,1,1335,68,1102,556,1,69,1101,1,0,71,1102,1337,1,72,1106,0,73,1,1733,29,481885,1102,1,38651,66,1101,0,1,67,1102,1366,1,68,1101,556,0,69,1101,5,0,71,1101,1368,0,72,1105,1,73,1,5,9,461915,31,281956,33,145954,33,218931,8,78158,1101,0,3389,66,1101,0,1,67,1102,1,1405,68,1102,1,556,69,1102,1,1,71,1102,1407,1,72,1106,0,73,1,283,16,208178,1102,1,45853,66,1101,0,1,67,1102,1,1436,68,1102,1,556,69,1102,1,1,71,1101,1438,0,72,1106,0,73,1,201,43,69346,1101,56453,0,66,1102,1,5,67,1101,1467,0,68,1102,1,302,69,1102,1,1,71,1102,1,1477,72,1106,0,73,0,0,0,0,0,0,0,0,0,0,27,2978,1101,0,72977,66,1101,4,0,67,1102,1,1506,68,1102,302,1,69,1102,1,1,71,1102,1,1514,72,1106,0,73,0,0,0,0,0,0,0,0,8,234474,1101,0,55061,66,1101,0,4,67,1102,1543,1,68,1102,253,1,69,1102,1,1,71,1101,0,1551,72,1106,0,73,0,0,0,0,0,0,0,0,3,16871,1101,0,37571,66,1102,1,1,67,1102,1580,1,68,1101,556,0,69,1101,0,6,71,1102,1582,1,72,1106,0,73,1,24874,27,1489,20,90887,20,181774,34,36353,34,72706,34,109059,1101,104089,0,66,1101,3,0,67,1101,0,1621,68,1102,302,1,69,1102,1,1,71,1101,1627,0,72,1105,1,73,0,0,0,0,0,0,29,289131,1101,0,71483,66,1101,1,0,67,1102,1,1656,68,1102,1,556,69,1101,0,1,71,1101,0,1658,72,1106,0,73,1,170,14,112906,1101,31793,0,66,1101,1,0,67,1101,0,1687,68,1102,1,556,69,1102,1,5,71,1102,1689,1,72,1106,0,73,1,1,16,312267,43,138692,19,3673,37,90271,14,169359,1102,1,21397,66,1101,1,0,67,1101,1726,0,68,1102,1,556,69,1102,1,1,71,1101,1728,0,72,1105,1,73,1,125,33,72977,1102,1,91571,66,1102,1,1,67,1101,0,1757,68,1102,1,556,69,1101,5,0,71,1102,1,1759,72,1105,1,73,1,3,43,104019,9,277149,31,352445,7,89867,7,269601,1102,1,23957,66,1101,0,2,67,1102,1796,1,68,1101,0,302,69,1102,1,1,71,1102,1,1800,72,1105,1,73,0,0,0,0,9,369532,1101,0,28669,66,1102,1,1,67,1102,1829,1,68,1101,556,0,69,1101,0,0,71,1101,0,1831,72,1105,1,73,1,1520,1102,1,90887,66,1102,3,1,67,1102,1,1858,68,1101,302,0,69,1102,1,1,71,1101,0,1864,72,1106,0,73,0,0,0,0,0,0,36,55061,1101,0,16871,66,1102,1,2,67,1102,1,1893,68,1101,351,0,69,1101,1,0,71,1102,1897,1,72,1106,0,73,0,0,0,0,255,37571,1102,43189,1,66,1102,1,1,67,1102,1926,1,68,1102,1,556,69,1101,1,0,71,1101,0,1928,72,1105,1,73,1,23,14,56453,1101,0,36353,66,1101,0,3,67,1102,1957,1,68,1101,0,302,69,1102,1,1,71,1102,1963,1,72,1105,1,73,0,0,0,0,0,0,36,165183,1101,0,39079,66,1101,6,0,67,1101,1992,0,68,1101,302,0,69,1102,1,1,71,1102,2004,1,72,1105,1,73,0,0,0,0,0,0,0,0,0,0,0,0,3,33742,1102,1,96377,66,1102,5,1,67,1102,1,2033,68,1102,253,1,69,1101,1,0,71,1101,2043,0,72,1106,0,73,0,0,0,0,0,0,0,0,0,0,1,47914,1101,0,70489,66,1102,5,1,67,1102,1,2072,68,1102,1,302,69,1101,0,1,71,1101,2082,0,72,1106,0,73,0,0,0,0,0,0,0,0,0,0,36,110122,1101,92383,0,66,1101,0,5,67,1102,1,2111,68,1101,302,0,69,1102,1,1,71,1102,2121,1,72,1106,0,73,0,0,0,0,0,0,0,0,0,0,31,140978,1101,0,69899,66,1101,0,1,67,1102,2150,1,68,1102,1,556,69,1101,1,0,71,1101,2152,0,72,1106,0,73,1,4929,29,385508,1101,0,84751,66,1101,1,0,67,1102,2181,1,68,1101,0,556,69,1101,0,1,71,1101,2183,0,72,1105,1,73,1,101,37,180542,1101,0,35159,66,1101,1,0,67,1102,2212,1,68,1102,556,1,69,1101,1,0,71,1101,2214,0,72,1105,1,73,1,160,8,117237,1102,31181,1,66,1101,0,1,67,1101,2243,0,68,1102,556,1,69,1102,1,0,71,1101,0,2245,72,1106,0,73,1,1796]

print ("23) answer part (a):", advent23a(advent23prog))   # 22877
print ("23) answer part (b):", advent23b(advent23prog))   # 15210
