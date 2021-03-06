# python3

# 5)

def domode(a, i, mode):
    if mode == 0:
        return a[i]
    elif mode == 1:
        return i
    
def intcomp5a(a):
    i = 0
    while True:
        code = "0000"+str(a[i])
        opcode = int(code[-2:])
        mode1 = int(code[-3:-2])
        mode2 = int(code[-4:-3])
        mode3 = int(code[-5:-4]) # Parameters that an instruction writes to will never be in immediate mode.
        #print ('code', code, opcode, mode1, mode2, mode3, a[i+1])
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
            a[i1] = int(input('Input number:'))
            i += 2
        elif opcode == 4:
            i1 = a[i+1]
            print ('Output number:', domode(a,i1,mode1))
            i += 2
        elif opcode == 99:
            break
        else:
            break
    
def intcomp5b(a):
    i = 0
    while True:
        code = "0000"+str(a[i])
        opcode = int(code[-2:])
        mode1 = int(code[-3:-2])
        mode2 = int(code[-4:-3])
        mode3 = int(code[-5:-4]) # Parameters that an instruction writes to will never be in immediate mode.
        #print ('code', code, opcode, mode1, mode2, mode3, a[i+1])
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
            a[i1] = int(input('Input number:'))
            i += 2
        elif opcode == 4:
            i1 = a[i+1]
            print ('Output number:', domode(a,i1,mode1))
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

advent5 = [3,225,1,225,6,6,1100,1,238,225,104,0,2,218,57,224,101,-3828,224,224,4,224,102,8,223,223,1001,224,2,224,1,223,224,223,1102,26,25,224,1001,224,-650,224,4,224,1002,223,8,223,101,7,224,224,1,223,224,223,1102,44,37,225,1102,51,26,225,1102,70,94,225,1002,188,7,224,1001,224,-70,224,4,224,1002,223,8,223,1001,224,1,224,1,223,224,223,1101,86,70,225,1101,80,25,224,101,-105,224,224,4,224,102,8,223,223,101,1,224,224,1,224,223,223,101,6,91,224,1001,224,-92,224,4,224,102,8,223,223,101,6,224,224,1,224,223,223,1102,61,60,225,1001,139,81,224,101,-142,224,224,4,224,102,8,223,223,101,1,224,224,1,223,224,223,102,40,65,224,1001,224,-2800,224,4,224,1002,223,8,223,1001,224,3,224,1,224,223,223,1102,72,10,225,1101,71,21,225,1,62,192,224,1001,224,-47,224,4,224,1002,223,8,223,101,7,224,224,1,224,223,223,1101,76,87,225,4,223,99,0,0,0,677,0,0,0,0,0,0,0,0,0,0,0,1105,0,99999,1105,227,247,1105,1,99999,1005,227,99999,1005,0,256,1105,1,99999,1106,227,99999,1106,0,265,1105,1,99999,1006,0,99999,1006,227,274,1105,1,99999,1105,1,280,1105,1,99999,1,225,225,225,1101,294,0,0,105,1,0,1105,1,99999,1106,0,300,1105,1,99999,1,225,225,225,1101,314,0,0,106,0,0,1105,1,99999,108,226,677,224,102,2,223,223,1005,224,329,1001,223,1,223,1107,677,226,224,102,2,223,223,1006,224,344,1001,223,1,223,7,226,677,224,1002,223,2,223,1005,224,359,101,1,223,223,1007,226,226,224,102,2,223,223,1005,224,374,101,1,223,223,108,677,677,224,102,2,223,223,1006,224,389,1001,223,1,223,107,677,226,224,102,2,223,223,1006,224,404,101,1,223,223,1108,677,226,224,102,2,223,223,1006,224,419,1001,223,1,223,1107,677,677,224,1002,223,2,223,1006,224,434,101,1,223,223,1007,677,677,224,102,2,223,223,1006,224,449,1001,223,1,223,1108,226,677,224,1002,223,2,223,1006,224,464,101,1,223,223,7,677,226,224,102,2,223,223,1006,224,479,101,1,223,223,1008,226,226,224,102,2,223,223,1006,224,494,101,1,223,223,1008,226,677,224,1002,223,2,223,1005,224,509,1001,223,1,223,1007,677,226,224,102,2,223,223,1005,224,524,1001,223,1,223,8,226,226,224,102,2,223,223,1006,224,539,101,1,223,223,1108,226,226,224,1002,223,2,223,1006,224,554,101,1,223,223,107,226,226,224,1002,223,2,223,1005,224,569,1001,223,1,223,7,226,226,224,102,2,223,223,1005,224,584,101,1,223,223,1008,677,677,224,1002,223,2,223,1006,224,599,1001,223,1,223,8,226,677,224,1002,223,2,223,1006,224,614,1001,223,1,223,108,226,226,224,1002,223,2,223,1006,224,629,101,1,223,223,107,677,677,224,102,2,223,223,1005,224,644,1001,223,1,223,8,677,226,224,1002,223,2,223,1005,224,659,1001,223,1,223,1107,226,677,224,102,2,223,223,1005,224,674,1001,223,1,223,4,223,99,226]

# 5a) MANUAL INPUT
# intcomp5a([3,0,4,0,99])    # input:1 output=1 ['1', 0, 4, 0, 99]
# intcomp5a([3,0,104,0,99])  # input:1 output=0 ['1', 0, 104, 0, 99]
print ("5) answer part (a):")
intcomp5a(advent5.copy()) # enter:1  9 x output:0 then output:6069343

# 5b) MANUAL INPUT
# intcomp5b([3,9,8,9,10,9,4,9,99,-1,8]) # position mode,  output 1 if input == 8; or else 0
# intcomp5b([3,9,7,9,10,9,4,9,99,-1,8]) # position mode,  output 1 if input <  8; or else 0
# intcomp5b([3,3,1108,-1,8,3,4,3,99])   # immediate mode, output 1 if input == 8; or else 0
# intcomp5b([3,3,1107,-1,8,3,4,3,99])   # immediate mode, output 1 if input <  8; or else 0
print ("5) answer part (b):")
intcomp5b(advent5.copy())  # enter:5  output:3188550
