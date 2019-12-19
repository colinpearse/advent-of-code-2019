# python3

# 18)

import os
import copy
import pickle

INF = 2*10000

class Path:
    def __init__(self, begin):
        self.nsteps = 0
        self.doors = set()
        self.tokey = [begin]

class KeyPath:
    def __init__(self, begin):
        self.nsteps = 0
        self.havekeys = [begin]

def readtext(file):
    return os.popen("cat "+file).read()

def read_maze(lines):
    maze = {}
    y = 0
    for line in lines.strip().split():
        x = 0
        for c in list(line):
            maze[(x,y)] = c
            x += 1
        y += 1
    return maze

def swapdict(d):
    return dict([(v,k) for k,v in d.items()])

def getkeys(revmaze):
    keys = []
    for c in list("abcdefghijklmnopqrstyvwxyz"):
        if c in revmaze:
            keys += [c]
    return keys

def possible_moves(maze, pos):
    x,y = pos
    moves = []
    for newpos in (x,y-1),(x,y+1),(x-1,y),(x+1,y):
        if newpos in maze and maze[newpos] != '#':
            moves.append(newpos)
    return moves

def get_door(maze, path, pos):
    if maze[pos] in list("ABCDEFGHIJKLMNOPQRSTYVWXYZ"):
        path.doors.add(maze[pos])
    return path

def get_paths(maze, paths, end):
    more_moves = False
    for path in paths.copy():
        if path.tokey[-1] == end:
            moves = []
        else:
            moves = possible_moves(maze, path.tokey[-1])
            moves = list(set(moves) - set(path.tokey))
        if moves:
            more_moves = True
            fmove = moves.pop()
            for move in moves:
                paths += [copy.deepcopy(path)]
                paths[-1].nsteps += 1
                paths[-1].tokey += [move]
                paths[-1] = get_door(maze, paths[-1], move)
            path.nsteps += 1
            path.tokey += [fmove]
            path = get_door(maze, path, fmove)
    return paths, more_moves

def get_shortest_path(paths, begin, end):
    shortest = float("inf")
    spath = None
    for path in paths:
        if path.tokey[0] == begin and path.tokey[-1] == end:
            if path.nsteps < shortest:
                shortest = path.nsteps
                spath = path
    return spath

def key2key(maze, k1, begin, k2, end):
    paths = [Path(begin)]
    more_moves = True
    while more_moves:
        paths,more_moves = get_paths(maze, paths, end)
    return get_shortest_path(paths, begin, end)

def k2k_map(maze, keys):
    revmaze = swapdict(maze)
    k2k = {}
    for i1 in range(len(keys)):
        for i2 in range(i1+1, len(keys)):
             k1 = keys[i1]
             k2 = keys[i2]
             path = key2key(maze, k1, revmaze[k1], k2, revmaze[k2])
             k2k[(k1,k2)] = (path.nsteps, path.doors)
    return k2k

def get_k2k(k2k, begin, end):
    if (begin,end) in k2k:
        return k2k[(begin,end)]
    else:
        return k2k[(end,begin)]

def save_k2k(k2k, k2kfile):
    fd = open(k2kfile, "wb")
    pickle.dump(k2k, fd)
    fd.close()

def load_k2k(loadfile, savefile, maze, allkeys):
    if loadfile != "":
        print ("loading pickle", loadfile)
        k2k = pickle.load(open(loadfile, "rb"))
    elif savefile != "":
        k2k = k2k_map(maze, allkeys)
        print ("saving pickle", savefile)
        save_k2k(k2k, savefile)
    else:
        k2k = k2k_map(maze, allkeys)
    return k2k
    
def find_steps(k2k, begin, nsteps, shsteps, keys, allkeys):
    print (nsteps, begin, keys)
    if set(keys) == set(allkeys):
        return nsteps, min(nsteps, shsteps)
    remkeys = list(set(allkeys) - set(keys))
    for end in remkeys:
        newsteps,doors = get_k2k(k2k,begin,end)
        if open_doors(doors, keys):
            nsteps, shsteps = find_steps(k2k, end, nsteps+newsteps, shsteps, keys+[end], allkeys)
            if shsteps != float("inf"):
                return nsteps, min(nsteps, shsteps)
    return nsteps, float("inf")

def open_door(doors, keys):
    for door in doors:
        if door.lower() not in keys:
            return False
    return True

def available_keys(k2k, bkey, allkeys, havekeys):
    ekeys = list(set(allkeys) - set(havekeys))
    avkeys = {}
    for ekey in ekeys:
        nsteps,doors = get_k2k(k2k,bkey,ekey)
        if open_door(doors, havekeys):
            avkeys[ekey] = nsteps
    return avkeys

def get_kpaths(k2k, kpaths, allkeys, topm=INF):
    more_moves = False
    for kpath in kpaths.copy():
        if set(kpath.havekeys) == set(allkeys):
            moves = {}
        else:
            moves = available_keys(k2k, kpath.havekeys[-1], allkeys, kpath.havekeys)
            moves = [(k,v) for k,v in sorted(moves.items(), key=lambda kv: kv[1])]
            if not moves:
                kpaths.remove(kpath)
        if moves:
            more_moves = True
            mlimit = 2
            fmove,fnsteps = moves[0]
            for move,nsteps in moves[1:topm]:
                kpaths += [copy.deepcopy(kpath)]
                kpaths[-1].havekeys += [move]
                kpaths[-1].nsteps   += nsteps
            kpath.havekeys += [fmove]
            kpath.nsteps   += fnsteps
    return kpaths, more_moves

def get_shortest_kpath(kpaths, bkey, allkeys):
    shortest = float("inf")
    for kpath in kpaths:
        if set(kpath.havekeys) == set(allkeys):
            shortest = min(kpath.nsteps, shortest)
    return shortest

def keypath(k2k, bkey, allkeys, topm=INF, topn=INF):
    kpaths = [KeyPath(bkey)]
    more_moves = True
    while more_moves:
        kpaths,more_moves = get_kpaths(k2k, kpaths, allkeys, topm=topm)
        kpaths = list(sorted(kpaths, key=lambda p: p.nsteps))[:topn]
    return get_shortest_kpath(kpaths, bkey, allkeys)

def advent18a(lines, loadfile="", savefile=""):
    maze     = read_maze(lines)
    revmaze  = swapdict(maze)
    allkeys  = getkeys(revmaze)
    havekeys = []
    begin    = '@'
    k2k      = load_k2k(loadfile, savefile, maze, allkeys+[begin])
    return keypath(k2k, begin, allkeys+[begin], topm=5, topn=1000)

advent18a_file = 'advent18a.txt'
eg1 = '''
#########
#b.A.@.a#
#########
'''
eg2 = '''
########################
#f.D.E.e.C.b.A.@.a.B.c.#
######################.#
#d.....................#
########################
'''
eg3 = '''
#################
#i.G..c...e..H.p#
########.########
#j.A..b...f..D.o#
########@########
#k.E..a...g..B.n#
########.########
#l.F..d...h..C.m#
#################
'''
eg4 = '''
########################
#@..............ac.GI.b#
###d#e#f################
###A#B#C################
###g#h#i################
########################
'''

# NOTE:
# As well as this taking too long to get the order the following logic is incorrect:
# The key to key paths (k2k) are not complete because I only get the shortest path for a unique key pair.
# I should be getting the shortest path for key pair and doors, ie ('a','h',['D','H']).

print ('shortest', advent18a(eg1))  # 8
print ('shortest', advent18a(eg2))  # 86
print ('shortest X', advent18a(eg3))  # 136
print ('shortest', advent18a(eg4))  # 81
print ('shortest X', advent18a(readtext(advent18a_file), loadfile="advent18a.pkl", savefile=""))

