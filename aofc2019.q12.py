# python3

# 12)

import re
import math

def mult(a):
    res = 1
    for e in a:
        res *= e
    return res

def factors(x):
    for y in range(2, int(x/2)):
        if x%y == 0:
            yield y

# least common multiple of all numbers in a
def lcm2(a, b):
    return abs(a*b) // math.gcd(a, b)

def lcm(a):
    currlcm = 1
    for e in a:
        currlcm = lcm2(currlcm, e)
    return currlcm

class Moons:
    def __init__(self, positions):
        self.moons = ["Io", "Europa", "Ganymede", "Callisto"]
        self.axes = ['x','y','z']
        self.mpos = self.set_mpos(positions)
        self.mvel = self.zero_mvel()
        self.recpos = self.initrec(self.mpos)
        self.recvel = self.initrec(self.mvel)
        self.pseqs = self.initseqs()
        self.vseqs = self.initseqs()
        
    def set_mpos(self, positions):       
        mposarr = re.sub(r'[>\n ]', '', positions, flags=re.M).split('<')[1:]
        mpos = {}
        for i in range(len(self.moons)):
            axmap = {}
            for axpos in mposarr[i].split(','):
                ax,pos = axpos.split('=')
                axmap[ax] = int(pos)
            mpos[self.moons[i]] = axmap
        return mpos

    def zero_mvel(self):
        mvel = {}
        for moon in self.moons:
            mvel[moon] = {'x':0, 'y':0, 'z':0}
        return mvel

    def initseqs(self):
        seqs = {}
        for moon in self.moons:
            seqs[moon] = {'x':0, 'y':0, 'z':0}
        return seqs
    
    def initrec(self, mvalues):
        rec = {}
        for moon in self.moons:
            rec[moon] = {'x':[mvalues[moon]['x']], 'y':[mvalues[moon]['y']], 'z':[mvalues[moon]['z']]}
        return rec

    def mprint(self):
        for moon in self.moons:
            print ("%-10.10s %-35.35s %s"%(moon, str(self.mpos[moon]), str(self.mvel[moon])))

    def rprint(self):
        for moon in self.moons:
            for ax in self.axes:
                print ("%-10.10s %s %s"%(moon, ax, str(self.recpos[moon][ax])))
            
    def chvel(self, ax1, ax2):
        if ax1 < ax2:
            return 1, -1
        elif ax1 > ax2:
            return -1, 1
        return 0, 0
    
    def step(self):
        for ax in self.axes:
            for i1 in range(len(self.moons)):
                for i2 in range(i1+1, len(self.moons)):
                    m1 = self.moons[i1]
                    m2 = self.moons[i2]
                    addv1, addv2 = self.chvel(self.mpos[m1][ax], self.mpos[m2][ax])
                    self.mvel[m1][ax] += addv1
                    self.mvel[m2][ax] += addv2

        for ax in self.axes:
            for moon in self.moons:
                self.mpos[moon][ax] += self.mvel[moon][ax]
                
    def record(self):
        for moon in self.moons:
            for ax in self.axes:
                self.recpos[moon][ax].append(self.mpos[moon][ax])
                self.recvel[moon][ax].append(self.mvel[moon][ax])

    def compare(self, i1, i2):
        for moon in self.moons:
            for ax in self.axes:
                if self.recpos[moon][ax][i1] != self.recpos[moon][ax][i2]:
                    return False
                if self.recvel[moon][ax][i1] != self.recvel[moon][ax][i2]:
                    return False
        return True
                
    def findseq(self, a):
        m = 10
        for i in range(1,int(len(a)/2)):
            if m < int(len(a)/2) and a[0:m] == a[i:i+m]:
                m *= 10
                if a[0:i] == a[i:i*2]:
                    return i
        return 0
    
    def getseqs(self):
        for moon in self.moons:
            for ax in self.axes:
                if self.pseqs[moon][ax] == 0:
                    self.pseqs[moon][ax] = self.findseq(self.recpos[moon][ax])
                if self.vseqs[moon][ax] == 0:
                    self.vseqs[moon][ax] = self.findseq(self.recvel[moon][ax])

    def printseqs(self):
        for moon in self.moons:
            for ax in self.axes:
                print (moon, ax, self.pseqs[moon][ax], self.vseqs[moon][ax])

    # get unique repititions
    def getureps(self):
        seqset = set()
        for moon in self.moons:
            for ax in self.axes:
                if self.pseqs[moon][ax] > 0 and self.vseqs[moon][ax] > 0:
                    seqset.add(self.pseqs[moon][ax])
                    seqset.add(self.vseqs[moon][ax])
                else:
                    return set()
        return seqset

    def steps(self, num, pr=0):
        for i in range(num):
            self.step()
            self.record()
            if pr == 1:   print (i+1); self.mprint()
            elif pr == 2: print ("%d) %-35.35s %s"%(i+1, str(self.mpos['Io']), str(self.mvel['Io'])))
            elif pr == 3: print ("%d) %-35.35s %s"%(i+1, str(self.mpos['Europa']), str(self.mvel['Europa'])))
            elif pr == 4: print ("%d) %-35.35s %s"%(i+1, str(self.mpos['Ganymede']), str(self.mvel['Ganymede'])))
            elif pr == 5: print ("%d) %-35.35s %s"%(i+1, str(self.mpos['Callisto']), str(self.mvel['Callisto'])))

    # potential (position) energy * kinetic energy
    def energy(self):
        potkin = 0
        for moon in self.moons:
            pot = sum(list(map(abs, self.mpos[moon].values())))
            kin = sum(list(map(abs, self.mvel[moon].values())))
            potkin += pot * kin
        return potkin


def advent12a(positions, nsteps):
    m = Moons(positions)
    m.mprint(); print ()
    m.steps(nsteps, pr=0)
    m.mprint()
    print ("energy =", m.energy(), '\n')

# find all the repeated sequences and find the lowest factor
def advent12b(positions, isteps=10):
    print ()
    m = Moons(positions)
    m.mprint(); print ()
    ureps = []
    tsteps = isteps
    while ureps == []:
        print ("do",tsteps,"more steps to find repeated pattern")
        m.steps(tsteps, pr=0)
        m.getseqs()
        #m.printseqs()
        ureps = list(m.getureps())
        tsteps *= isteps
    return lcm(ureps)

    
eg1 = '''
<x=-1, y=0, z=2>
<x=2, y=-10, z=-7>
<x=4, y=-8, z=8>
<x=3, y=5, z=-1>
'''
eg2 = '''
<x=-8, y=-10, z=0>
<x=5, y=5, z=10>
<x=2, y=-7, z=3>
<x=9, y=-8, z=-3>
'''

advent12a_input = '''
<x=-7, y=17, z=-11>
<x=9, y=12, z=5>
<x=-9, y=0, z=-4>
<x=4, y=6, z=0>
'''

advent12a(eg1, 10)    # 179
advent12a(eg2, 100)   # 1940
print ("11) answer part (a):")
advent12a(advent12a_input, 1000)   # 7013

print (advent12b(eg1))  # 2772
print (advent12b(eg2))  # 4686774924
print ("11) answer part (b):",advent12b(advent12a_input))   # 324618307124784
