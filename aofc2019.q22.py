# python3

# 22)

import os
import sys
import copy

# O(1) setting ni using i
# NOTE: n is picked specifically so it does not not overlap cards
def _deal_with_inc(cards, n):
    lenc = len(cards)
    ncards = [-1] * lenc
    ni = 0
    for i in range(0,len(cards)):
        ni = (i*n) - int((i*n)/lenc)*lenc
        ncards[ni] = cards[i]
    return ncards

def _deal_into_new_stack(cards):
    return cards[::-1]

def _cut(cards, n):
    return cards[n:]+cards[:n]

# TEST deal/stack/cut i2ni_... functions work - ie. they can replace those above for problem (a)
def i2ni(cards, func, n=None):
    lenc = len(cards)
    ncards = [-1] * lenc
    for i in range(0,len(cards)):
        ni = func(lenc, n, i)
        ncards[ni] = cards[i]
    return ncards
def deal_with_inc(cards, n):
    return i2ni(cards, i2ni_inc, n=n)
def deal_into_new_stack(cards):
    return i2ni(cards, i2ni_stack)
def cut(cards, n):
    return i2ni(cards, i2ni_cut, n=n)

# get ni from i - all functions are O(1)
#i2ni_inc   = lambda lenc,n,i: (i*n) - int((i*n)/lenc)*lenc
#i2ni_stack = lambda lenc,n,i: lenc - i - 1
#i2ni_cut   = lambda lenc,n,i: (lenc-n+i if i<n else i-n) if n>=0 else (lenc-(lenc+n)+i if i<(lenc+n) else i-(lenc+n))

def i2ni_inc(lenc, n, i):
    return (i*n) - int((i*n)/lenc)*lenc
def i2ni_stack(lenc, n, i):
    return lenc - i - 1
def i2ni_cut(lenc, n, i):
    if n < 0:
        n = lenc + n
    if i >= n:
        return i - n
    else:
        return lenc - n + i

# (reverse) get i from ni - all functions are O(1)
#def ni2i_stack(lenc, n, ni):
#    return lenc - ni - 1

def check_cards(cards, olen):
    if -1 in cards:        print ("ERROR: -1 found in cards - check deal_with_inc()")
    if olen != len(cards): print ("ERROR: original length differs from actual length", olen, "vs", len(cards))

# for (b)
# Very Large Card Array (alen is hard limit)
class VLCA:
    def __init__(self, arg1=0, seti=[]):
        self.__defval = -1
        if isinstance(arg1, int):
            self.__first = True
            self.__alen = arg1
            self.__a = {}
            self.havei = set(seti)
            #self.needi = set()
            #self.needalli = set()
            for i in seti:
                self.__a[i] = i
        elif isinstance(arg1, VLCA):
            self.__first = False
            self.__defval = -1
            self.__alen = len(arg1)
            self.__a    = {}
            self.havei  = set()
            #self.needi  = set()
            #self.needalli = set(arg1.needalli) | set(arg1.needi)

    def getfirst(self):
        return self.__first

    def p(self, f, t):
        a = []
        for i in range(f, t+1):
            a += [self.__getitem__(i)]
        return str(a)
        
    def copya(self):
        a = {}
        for k,v in self.__a.items():
            a[k] = v
        return a

    def __checkalen(self, idx):
        if idx < 0 or idx+1 > self.__alen: raise Exception(idx)

    def __len__(self):
        return self.__alen

    def __setitem__(self, idx, val):
        self.__checkalen(idx)
        self.__a[idx] = val
        self.havei.add(idx)

    def __getitem__(self, idx):
        self.__checkalen(idx)
        val = self.__defval
        if self.__first:
            self.__a[idx] = idx
            self.havei.add(idx)
            val = idx
        else:
            if idx in self.havei:
                val = self.__a[idx]
            #else:
            #    self.needi.add(idx)
        return val

def readtext(file):
    return os.popen("cat "+file).read()

def advent22a(cards, shuffle):
    cardslen = len(cards)
    for shuf in shuffle:
        #print (shuf)
        shufa = shuf.split()
        if   shufa[0] == 'cut':       cards = cut(cards, int(shufa[1]))           #; print ('cut', int(shufa[1]), cards)
        elif shufa[2] == 'new':       cards = deal_into_new_stack(cards)          #; print ('new stack', cards)
        elif shufa[2] == 'increment': cards = deal_with_inc(cards, int(shufa[3])) #; print ('incr', int(shufa[3]), cards)
    check_cards(cards, cardslen)
    return cards.index(2019) if len(cards) == 10007 else cards

# Halley's comet a clue?  orbital period: 75.32y discovered:1758  rotation:2.2d 52.8h
# Q: can I convert each shuffle part to an expression and use my VLA() class (changed to use expression to return the value)?
#    then I could work on the first 5 cards and various other cards in the deck as and when needed
#
# working backwards, if I want the cards for the first five positions [0..4]
#   deal with increment 33 - I would need indexes [a1,b1,c1,d1,e1] to make [0..4]
#   cut -8040              - I would need indexes [a2,b2,c2,d2,e2] to make [a1,b1,c1,d1,e1]
#   deal into new stack    - I would need indexes [a3,b3,c3,d3,e3] to make [a2,b2,c2,d2,e2]
#   ... to the start ...
#   deal with increment 26 - I would need indexes [a100,b100,c100,d100,e100] to make [a99,b99,c99,d99,e99]
#
#   ... then repeat until [a100,b100,c100,d100,e100] indexes are repeated. If they repeat.
# "find" are the result index(es) I'm interested in.
# So work backwards, tracking indexes, finally reaching those index(es) with which I need to start.
def advent22b(cardsqty, shuffleqty, shuffle):
    ni = 0  # starting index
    pni = ni
    for count in range(0, shuffleqty):
        for shuf in shuffle:
            shufa = shuf.split()
            if   shufa[0] == 'cut':       ni = i2ni_cut(cardsqty, int(shufa[1]), ni)
            elif shufa[2] == 'new':       ni = i2ni_stack(cardsqty, None, ni)
            elif shufa[2] == 'increment': ni = i2ni_inc(cardsqty, int(shufa[3]), ni)
        if count < 10:
            print ("0, after shuffle", count, ",", pni, "->", ni, "diff", ni-pni, "diff%1000", (ni-pni)%1000)
        else:
            break
        pni = ni
    return -1

    #cards = VLCA(cardsqty, find)
    #for shuf in shuffle[::-1]:
    #    print (shuf)
    #    shufa = shuf.split()
    #    if   shufa[0] == 'cut':       ncards = reverse_cut(cards, int(shufa[1]))           #; print ('cut', int(shufa[1]), cards.p(3,4))
    #    elif shufa[2] == 'new':       ncards = reverse_deal_into_new_stack(cards)          #; print ('new stack', cards.p(3,4))
    #    elif shufa[2] == 'increment': ncards = reverse_deal_with_inc(cards, int(shufa[3])) #; print ('incr', int(shufa[3]), cards.p(3,4))
    #    print ('cards I would need to find', cards.havei, 'are', ncards.havei)
    #    cards = ncards
    #havei = cards.havei

    #cards = VLCA(cardsqty, list(havei))
    #for shuf in shuffle:
    #    print (shuf)
    #    shufa = shuf.split()
    #    if   shufa[0] == 'cut':       cards = minimal_cut(cards, int(shufa[1]))           #; print ('cut', int(shufa[1]), cards.p(3,4))
    #    elif shufa[2] == 'new':       cards = minimal_deal_into_new_stack(cards)          #; print ('new stack', cards.p(3,4))
    #    elif shufa[2] == 'increment': cards = minimal_deal_with_inc(cards, int(shufa[3])) #; print ('incr', int(shufa[3]), cards.p(3,4))
    ##return cards.index(2019) if len(cards) == 10007 else cards
    #return [cards[3],cards[4]]

egcards = list(range(10))
eg1shuffle = '''
deal with increment 7
deal into new stack
deal into new stack
'''
eg2shuffle = '''
cut 6
deal with increment 7
deal into new stack
'''
eg3shuffle = '''
deal with increment 7
deal with increment 9
cut -2
'''
eg4shuffle = '''
deal into new stack
cut -2
deal with increment 7
cut 8
cut -4
deal with increment 7
cut 3
deal with increment 9
deal with increment 3
cut -1
'''

advent22a_cards = list(range(10007))
advent22a_file = 'advent22a.txt'

advent22b_cards   = 119315717514047
advent22b_shuffle = 101741582076661

#print (deal_with_inc(list(range(20)), 7))
#sys.exit (0)

print (advent22a(egcards, eg1shuffle.splitlines()[1:]))   # 0 3 6 9 2 5 8 1 4 7
print (advent22a(egcards, eg2shuffle.splitlines()[1:]))   # 3 0 7 4 1 8 5 2 9 6
print (advent22a(egcards, eg3shuffle.splitlines()[1:]))   # 6 3 0 7 4 1 8 5 2 9
print (advent22a(egcards, eg4shuffle.splitlines()[1:]))   # 9 2 5 8 1 4 7 0 3 6
print ("22) answer part (a):", advent22a(advent22a_cards, readtext(advent22a_file).splitlines()))   # index of card 2019: 6289

#print ("22) answer part (b):", advent22b(len(egcards), 1, eg1shuffle.splitlines()[1:], [3,4]))  # 0 3 6 9 2
print ("22) answer part (b):", advent22b(advent22b_cards, advent22b_shuffle, readtext(advent22a_file).splitlines()))  # card at index [2020]: 

