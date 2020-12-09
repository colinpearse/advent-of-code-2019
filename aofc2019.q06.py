# python3

# 6)

import csv
def readfile(file):
    with open(file) as fd:
        lines = list(csv.reader(fd, delimiter=')'))
    return lines

def count_orbits(satmap, sat):
    orbit = 0
    while sat in satmap:
        orbit += 1
        sat = satmap[sat]
    return orbit
    
def calc_orbits(orbpairs):
    satmap = dict([(sat,obj) for obj,sat in iter(orbpairs)])
    orbits = 0
    for sat in satmap.keys():
        orbits += count_orbits(satmap, sat)
    return orbits

def get_objlist(satmap, sat):
    objlist = []
    while sat in satmap:
        sat = satmap[sat]
        objlist.append(sat)
    return objlist

def closest_orb(sorbs, eorbs):
    set_eorbs = set(eorbs)
    for orb in sorbs:
        if orb in set_eorbs:
            return orb
    return None

def count_orb(orbs, torb):
    for i,orb in enumerate(orbs):
        if orb == torb:
            return i
    return -1

def calc_orbitals(orbpairs, start, end):
    satmap = dict([(sat,obj) for obj,sat in iter(orbpairs)])
    sorbs = get_objlist(satmap, start)
    eorbs = get_objlist(satmap, end)
    orb = closest_orb(sorbs, eorbs)
    scount = count_orb(sorbs, orb)
    ecount = count_orb(eorbs, orb)
    return scount + ecount

advent6a_eg1 = [['COM','B'],['B','C'],['C','D'],['D','E'],['E','F'],['B','G'],['G','H'],['D','I'],['E','J'],['J','K'],['K','L']]
advent6a = readfile('aofc2019.06a.txt')

advent6b_eg1 = [['COM','B'],['B','C'],['C','D'],['D','E'],['E','F'],['B','G'],['G','H'],['D','I'],['E','J'],['J','K'],['K','L'],['K','YOU'],['I','SAN']]
advent6b = readfile('aofc2019.06a.txt')

print (calc_orbits(advent6a_eg1))  # 42
print ("6) answer part (a):", calc_orbits(advent6a))      # 194721

print (calc_orbitals(advent6b_eg1, 'YOU', 'SAN'))      # 4
print ("6) answer part (b):", calc_orbitals(advent6b, 'YOU', 'SAN'))      # 316
