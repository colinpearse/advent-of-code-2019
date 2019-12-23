# python3

# 22)

import os
import sys

# formula works for 10 cards but no more
def BADdeal_with_inc(cards, n):
    lenc = len(cards)
    ncards = [-1] * lenc
    ni = 0
    for i in range(0,len(cards)):
        ni = ((lenc-n)*i)%10
        ncards[i] = cards[ni]
    return ncards

# n is picked specifically so it does not not overlap cards
def OLDdeal_with_inc(cards, n):
    ncards = [-1] * len(cards)
    ni = 0
    for c in cards:
        ncards[ni] = c
        if ni+n < len(cards):
            ni += n
        else:
            ni = ni+n-len(cards)
    return ncards

def deal_with_inc(cards, n):
    ncards = [-1] * len(cards)
    ni = 0
    for i in range(0,len(cards)):
        ncards[ni] = cards[i]
        ni = (ni+n)%len(cards)
    return ncards

def deal_into_new_stack(cards):
    return cards[::-1]

def cut(cards, n):
    return cards[n:]+cards[:n]

def check_cards(cards, olen):
    if -1 in cards:        print ("ERROR: -1 found in cards - check deal_with_inc()")
    if olen != len(cards): print ("ERROR: original length differs from actual length", olen, "vs", len(cards))

def readtext(file):
    return os.popen("cat "+file).read()

def advent22a(cards, shuffle):
    olen = len(cards)
    for shuf in shuffle:
        #print (shuf)
        shufa = shuf.split()
        if   shufa[0] == 'cut':       ncards = cut(cards, int(shufa[1]));          #; print ('cut', int(shufa[1]), cards)
        elif shufa[2] == 'new':       ncards = deal_into_new_stack(cards)          #; print ('new stack', cards)
        elif shufa[2] == 'increment': ncards = deal_with_inc(cards, int(shufa[3])) #; print ('incr', int(shufa[3]), cards)
        cards = ncards
    check_cards(cards, olen)
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
def advent22b(cardsqty, shuffleqty, shuffle):
    #advent22a_cards, readtext(advent22a_file).splitlines()
    olen = cardsqty
    for shuf in shuffle:
        #print (shuf)
        shufa = shuf.split()
        if   shufa[0] == 'cut':       ncards = minimal_cut(cards, int(shufa[1]));          #; print ('cut', int(shufa[1]), cards)
        elif shufa[2] == 'new':       ncards = minimal_deal_into_new_stack(cards)          #; print ('new stack', cards)
        elif shufa[2] == 'increment': ncards = minimal_deal_with_inc(cards, int(shufa[3])) #; print ('incr', int(shufa[3]), cards)
        cards = ncards
        #print ()
    check_cards(cards, olen)
    #return cards.index(2019) if len(cards) == 10007 else cards
    return "no solution yet"

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

#print ("22) answer part (b):", advent22b(advent22b_cards, advent22b_shuffle, eg1shuffle.splitlines()[1:]))  # 0 3 6 9 2
#print ("22) answer part (b):", advent22b(advent22b_cards, advent22b_shuffle, readtext(advent22a_file).splitlines()))  # card at index [2020]: 

