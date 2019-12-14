# python3

# 14)

import os

def readtext(file):
    return os.popen("cat "+file).read()

# FUEL 1 {(7, 'A'), (1, 'E')}
# A 10 {(10, 'ORE')}
# C 1 {(7, 'A'), (1, 'B')}
def get_reaction(line):
    reaction = line.split(' => ')
    chemicals = reaction[0].split(', ')
    result = reaction[1].split(' ')
    qty,rchem = result[0],result[1]
    setchems = set(map(lambda qc:(int(qc[0]),qc[1]), [tuple(qc.split(' ')) for qc in chemicals]))
    return rchem, qty, setchems
        
def make_reactions(data):
    reactions = {}
    for line in data.strip().split('\n'):
        rchem, qty, setchems = get_reaction(line)
        reactions[rchem] = {}
        reactions[rchem][qty] = setchems
    return reactions

# if loops is enormous it can be reduced. The last few iterations are done one by one to
# ensure this test "have[chem] >= need[chem]" in calc_ore() fails at the appropriate time
def shortcut_loops(loops, limit):
    if loops > limit:
        m = loops - (limit-1)
        loops -= m
    else:
        m = 1
        loops -= 1
    return m, loops

def calc_ore(reactions, chem, needq, have, need):
    if chem not in need: need[chem] = 0
    if chem not in have: have[chem] = 0
    need[chem] += needq

    if chem in reactions:
        prodq = int(list(reactions[chem].keys())[0])  # only 1 number
        chems = list(reactions[chem].values())[0]     # only 1 set of tuples
        loops = int((needq+prodq-1)/prodq)            # eg (0,12,7) loops=2 since I need a minimum of 12
        m = 1
        while loops > 0:
            if have[chem] >= need[chem]:
                break
            m, loops = shortcut_loops(loops, 5)
            have[chem] += prodq*m
            for q,c in chems:
                have, need = calc_ore(reactions, c, q*m, have, need)
    return have, need

def get_waste(have, need, fuel, ore):
    waste = {}
    for chem in have:
        waste[chem] = (have[chem] - need[chem]) * fuel
    waste['ORE'] = ore
    return waste

def convert_waste(reactions, waste):
    can_convert = True
    while can_convert:
        can_convert = False
        for chem in waste:
            if chem == 'ORE':
                continue
            prodq = int(list(reactions[chem].keys())[0])  # only 1 number
            chems = list(reactions[chem].values())[0]     # only 1 set of tuples
            mult = int(waste[chem] / prodq)
            if mult > 0:
                can_convert = True
                waste[chem] -= (prodq * mult)
                for q,c in chems:
                    waste[c] += (q * mult)
    return waste

def advent14a(data, fuel=1):
    have = {}
    need = {}
    reactions = make_reactions(data)
    have, need = calc_ore(reactions, 'FUEL', fuel, have, need)
    return need['ORE']

def advent14b(data, initore=1000000000000):
    have = {}
    need = {}
    reactions = make_reactions(data)
    have, need = calc_ore(reactions, 'FUEL', 1, have, need)
    tfuel = 0
    fuel = 1
    ore = initore
    while fuel > 0:
        fuel = int(ore / need['ORE'])
        rore = int(ore % need['ORE'])
        tfuel += fuel
        waste = get_waste(have, need, fuel, rore)
        waste = convert_waste(reactions, waste)
        ore = waste['ORE']
    # fine tune convert_waste loop
    while advent14a(data, fuel=tfuel) < initore:
        tfuel += 1
    return tfuel-1

    
eg1 = '''
10 ORE => 10 A
1 ORE => 1 B
7 A, 1 B => 1 C
7 A, 1 C => 1 D
7 A, 1 D => 1 E
7 A, 1 E => 1 FUEL
'''
eg2 = '''
157 ORE => 5 NZVS
165 ORE => 6 DCFZ
44 XJWVT, 5 KHKGT, 1 QDVJ, 29 NZVS, 9 GPVTF, 48 HKGWZ => 1 FUEL
12 HKGWZ, 1 GPVTF, 8 PSHF => 9 QDVJ
179 ORE => 7 PSHF
177 ORE => 5 HKGWZ
7 DCFZ, 7 PSHF => 2 XJWVT
165 ORE => 2 GPVTF
3 DCFZ, 7 NZVS, 5 HKGWZ, 10 PSHF => 8 KHKGT
'''
advent14a_data = "advent14a.txt"

print (advent14a(eg1))  # 31
print (advent14a(eg2))  # 13312
print ("13) answer part (a):",advent14a(readtext(advent14a_data)))  # 114125

print ()
print (advent14b(eg2))  # 82892753
print ("13) answer part (b):",advent14b(readtext(advent14a_data)))  # 12039407
