# python

#%%time
# SLOW_phase = 22s for 650 string (using ifs instead of map gained only a second)
# FAST_phase = 13s for 650 string
# NUMPY_phase = 50s for 650 string
# WHY_phase  = why does this work phase - I guess properties of a wave, fft was the clue I suppose
# 
# 16) shortcut using start == offset, but still too slow

def SLOW_phase(numstr, start=1, end=-1):
    a = list(map(int, list(numstr)))
    lena = len(a)
    if end == -1: end = lena+1
    pattern = {0:0, 1:1, 2:0, 3:-1}
    res = []
    for i in range(start, end):
        digit = 0
        for j in range(start, end):
            digit += a[j-1] * pattern[int(j/i)%4]
        res.append(list(str(digit))[-1])
    return ''.join(res)

# I've tried passing int array so I don't have to convert it - not much improvement
def FAST_phase(numstr, start=1, end=-1):
    a = list(map(int, list(numstr)))
    lena = len(a)
    if end == -1: end = lena+1
    res = []
    for i in range(start, end):
        pattern = [0]*i + [1]*i + [0]*i + [-1]*i
        rpattern = list(pattern * ((int(lena / len(pattern))) + 1))[start:end]
        res.append(list(str(sum([a[j-1] * rpattern[j-start] for j in range(start,end)])))[-1])
    return ''.join(res)

def WHY_phase(numstr):
    a = list(map(int, list(numstr)))
    suma = sum(a)
    res = []
    for e in a:
        res.append(suma%10)
        suma -= e
    return ''.join(list(map(str,res)))

# VERY SLOW
# import numpy as np
# def NUMPY_phase(numstr, start=1, end=1):
#     a = list(map(int, list(numstr)))
#     lena = len(a)
#     a = np.array(a)
#     res = []
#     for i in range(start, end):
#         pattern = [0]*i + [1]*i + [0]*i + [-1]*i
#         rpattern = np.array(list(pattern * ((int(lena / len(pattern))) + 1))[1:lena+1])
#         res.append(str(sum(list(map(lambda e:int(str(e)[-1]), np.multiply(a, rpattern).tolist()))))[-1])
#     return ''.join(res)

def nphases(numstr, phases):
    for i in range(1,phases+1):
        numstr = FAST_phase(numstr)
    return numstr

def advent16a(numstr, phases=100):
    return nphases(numstr, phases)[0:8]

def advent16b(numstr, m=1, oset=7, phases=100):
    offset = int(numstr[0:oset])
    numstr = list(numstr * m)[offset:]
    for i in range(phases):
        numstr = WHY_phase(numstr)
    return numstr[0:8]

advent16 = '59782619540402316074783022180346847593683757122943307667976220344797950034514416918778776585040527955353805734321825495534399127207245390950629733658814914072657145711801385002282630494752854444244301169223921275844497892361271504096167480707096198155369207586705067956112600088460634830206233130995298022405587358756907593027694240400890003211841796487770173357003673931768403098808243977129249867076581200289745279553289300165042557391962340424462139799923966162395369050372874851854914571896058891964384077773019120993386024960845623120768409036628948085303152029722788889436708810209513982988162590896085150414396795104755977641352501522955134675'
        
print (advent16a('12345678', phases=4))   # 01029498
print (advent16a('80871224585914546619083218645595', phases=100))  # 24176176
print (advent16a('19617804207202209144916044189917', phases=100))  # 73745418
print (advent16a('69317163492948606335995924319873', phases=100))  # 52432133
print ("16) answer part (a):", advent16a(advent16, phases=100))    # 27229269

print ()
print (advent16b('03036732577212944063491565474664', m=10000, oset=7, phases=100))   # 84462026
print (advent16b('02935109699940807407585447034323', m=10000, oset=7, phases=100))   # 78725270
print (advent16b('03081770884921959731165446850517', m=10000, oset=7, phases=100))   # 53553731
print ("16) answer part (b):", advent16b(advent16, m=10000, oset=7, phases=100))   # 26857164
