# python3

# 7)
import collections
import itertools

def domode(a, i, mode):
    if mode == 0:
        return a[i]
    elif mode == 1:
        return i
    
def intcomp7a(a, I=[], auto=True):
    O = []
    i = 0
    while True:
        code = "0000"+str(a[i])
        opcode = int(code[-2:])
        mode1 = int(code[-3:-2])
        mode2 = int(code[-4:-3])
        mode3 = int(code[-5:-4]) # Parameters that an instruction writes to will never be in immediate mode.
        if opcode == 1:
            i1,i2,i3 = a[i+1],a[i+2],a[i+3]
            a[i3] = domode(a,i1,mode1) + domode(a,i2,mode2)
            i += 4
        elif opcode == 2:
            i1,i2,i3 = a[i+1],a[i+2],a[i+3]
            a[i3] = domode(a,i1,mode1) * domode(a,i2,mode2)
            i += 4
        elif opcode == 3:
            i1 = a[i+1]
            if auto == True:
                if I:
                    a[i1] = I.pop()
                else:
                    # I need to return and wait for output - how?
                    print ("input")
            else:
                a[i1] = int(input('Input number:'))
            i += 2
        elif opcode == 4:
            i1 = a[i+1]
            O.append(domode(a,i1,mode1))
            if auto == False:
                print('Output number:', domode(a,i1,mode1))
            i += 2
        elif opcode == 5:
            i1,i2 = a[i+1],a[i+2]
            i = domode(a,i2,mode2) if domode(a,i1,mode1) else i+3
        elif opcode == 6:
            i1,i2 = a[i+1],a[i+2]
            i = domode(a,i2,mode2) if not domode(a,i1,mode1) else i+3
        elif opcode == 7:
            i1,i2,i3 = a[i+1],a[i+2],a[i+3]
            a[i3] = 1 if domode(a,i1,mode1) < domode(a,i2,mode2) else 0
            i += 4
        elif opcode == 8:
            i1,i2,i3 = a[i+1],a[i+2],a[i+3]
            a[i3] = 1 if domode(a,i1,mode1) == domode(a,i2,mode2) else 0
            i += 4
        elif opcode == 99:
            break
        else:
            raise Exception(opcode)
    return O[-1]

def phase(prog, seq, r=0):
    for s in seq:
        r = intcomp7a(prog, I=[r,s])
    return r

def advent7a(prog, initr=0):
    maxr = float("-inf")
    for p1,p2,p3,p4,p5 in itertools.permutations(list(range(5))):
        cprog = prog.copy()
        r = phase(cprog, [p1,p2,p3,p4,p5], r=initr)
        maxr = max(maxr,r)
    return maxr


# this needs to freeze the state and restart where it left off
def intcomp7b(a, i=0, I=[]):
    Ii = 0
    O = []
    while True:
        code = "0000"+str(a[i])
        opcode = int(code[-2:])
        mode1 = int(code[-3:-2])
        mode2 = int(code[-4:-3])
        mode3 = int(code[-5:-4]) # Parameters that an instruction writes to will never be in immediate mode.
        if opcode == 1:
            i1,i2,i3 = a[i+1],a[i+2],a[i+3]
            a[i3] = domode(a,i1,mode1) + domode(a,i2,mode2)
            i += 4
        elif opcode == 2:
            i1,i2,i3 = a[i+1],a[i+2],a[i+3]
            a[i3] = domode(a,i1,mode1) * domode(a,i2,mode2)
            i += 4
        elif opcode == 3:
            i1 = a[i+1]
            if Ii < len(I):
                a[i1] = I[Ii]
                Ii += 1
            else:
                return O[-1], i  # no input so return state+freeze
            i += 2
        elif opcode == 4:
            i1 = a[i+1]
            O.append(domode(a,i1,mode1))
            #print('output:', domode(a,i1,mode1))
            i += 2
        elif opcode == 5:
            i1,i2 = a[i+1],a[i+2]
            i = domode(a,i2,mode2) if domode(a,i1,mode1) else i+3
        elif opcode == 6:
            i1,i2 = a[i+1],a[i+2]
            i = domode(a,i2,mode2) if not domode(a,i1,mode1) else i+3
        elif opcode == 7:
            i1,i2,i3 = a[i+1],a[i+2],a[i+3]
            a[i3] = 1 if domode(a,i1,mode1) < domode(a,i2,mode2) else 0
            i += 4
        elif opcode == 8:
            i1,i2,i3 = a[i+1],a[i+2],a[i+3]
            a[i3] = 1 if domode(a,i1,mode1) == domode(a,i2,mode2) else 0
            i += 4
        elif opcode == 99:
            break
        else:
            raise Exception(opcode)
    return O[-1], 0

def phase_feedback(prog, seq, r=0):
    progs = [prog.copy() for i in range(len(seq))]
    pptrs = [0 for i in range(len(seq))]
    out   = [r for i in range(len(seq))]
    res = -1
    for c in itertools.count():
        for i in range(len(seq)):
            if c == 0:
                res,pptrs[i] = intcomp7b(progs[i], i=pptrs[i], I=[seq[i],out[i]])
            else:
                res,pptrs[i] = intcomp7b(progs[i], i=pptrs[i], I=[out[i]])
            out[((i+1)%len(seq))] = res

        if set(pptrs) == set([0]):
            break
       
    return res

def advent7b(prog, initr=0):
    maxr = float("-inf")
    for p1,p2,p3,p4,p5 in itertools.permutations(list(range(5,10))):
        cprog = prog.copy()
        r = phase_feedback(cprog, [p1,p2,p3,p4,p5], r=initr)
        maxr = max(maxr,r)
    return maxr

advent7prog = [3,8,1001,8,10,8,105,1,0,0,21,34,55,68,93,106,187,268,349,430,99999,3,9,102,5,9,9,1001,9,2,9,4,9,99,3,9,1001,9,5,9,102,2,9,9,101,2,9,9,102,2,9,9,4,9,99,3,9,101,2,9,9,102,4,9,9,4,9,99,3,9,101,4,9,9,102,3,9,9,1001,9,2,9,102,4,9,9,1001,9,2,9,4,9,99,3,9,101,2,9,9,1002,9,5,9,4,9,99,3,9,101,1,9,9,4,9,3,9,1002,9,2,9,4,9,3,9,1002,9,2,9,4,9,3,9,1002,9,2,9,4,9,3,9,101,2,9,9,4,9,3,9,1001,9,2,9,4,9,3,9,1002,9,2,9,4,9,3,9,102,2,9,9,4,9,3,9,1002,9,2,9,4,9,3,9,101,1,9,9,4,9,99,3,9,101,2,9,9,4,9,3,9,1001,9,1,9,4,9,3,9,101,1,9,9,4,9,3,9,1001,9,1,9,4,9,3,9,1001,9,2,9,4,9,3,9,102,2,9,9,4,9,3,9,1001,9,1,9,4,9,3,9,102,2,9,9,4,9,3,9,1001,9,1,9,4,9,3,9,101,2,9,9,4,9,99,3,9,102,2,9,9,4,9,3,9,102,2,9,9,4,9,3,9,1002,9,2,9,4,9,3,9,1002,9,2,9,4,9,3,9,1002,9,2,9,4,9,3,9,101,1,9,9,4,9,3,9,101,1,9,9,4,9,3,9,101,1,9,9,4,9,3,9,101,2,9,9,4,9,3,9,1001,9,2,9,4,9,99,3,9,1002,9,2,9,4,9,3,9,1002,9,2,9,4,9,3,9,1001,9,2,9,4,9,3,9,1002,9,2,9,4,9,3,9,1002,9,2,9,4,9,3,9,101,2,9,9,4,9,3,9,1001,9,2,9,4,9,3,9,101,1,9,9,4,9,3,9,101,1,9,9,4,9,3,9,101,1,9,9,4,9,99,3,9,101,2,9,9,4,9,3,9,1002,9,2,9,4,9,3,9,1002,9,2,9,4,9,3,9,101,1,9,9,4,9,3,9,1001,9,1,9,4,9,3,9,101,2,9,9,4,9,3,9,1002,9,2,9,4,9,3,9,1002,9,2,9,4,9,3,9,1002,9,2,9,4,9,3,9,1002,9,2,9,4,9,99]

eg1 = [3,15,3,16,1002,16,10,16,1,16,15,15,4,15,99,0,0]
seq1 = [4,3,2,1,0]
print (phase(eg1, seq1)) # 43210 - from phase setting sequence 
print ("7) answer part (a):",advent7a(advent7prog))  # answer a: 34852

eg2 = [3,26,1001,26,-4,26,3,27,1002,27,2,27,1,27,26,27,4,27,1001,28,-1,28,1005,28,6,99,0,0,5]
seq2 = [9,8,7,6,5]
print (phase_feedback(eg2, seq2)) # 139629729
print ("7) answer part (b):",advent7b(advent7prog))  # answer b: 44282086
