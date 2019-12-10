# python3

# 4)

def validpw_a(num):
    numarr = list(map(int, list(str(num))))
    numdig = len(numarr)
    if numdig == 6:
        lastdig = 0
        doubdig = False
        for dig in numarr:
            if dig == lastdig:
                doubdig = True
            elif dig > lastdig:
                lastdig = dig
            else:
                return False
        return doubdig
    return False
    
def hasdouble(numarr):
    return (set(numarr) & set({2}) == set({2}))
    #return not sum(set(map(lambda n: n%2, numset - set({1}))))
    
# only even number of doubles allowed
def validpw_b(num):
    numarr = list(map(int, list(str(num))))
    numdig = len(numarr)
    if numdig == 6:
        lastdig = 0
        doubdig = {0:1, 1:1, 2:1, 3:1, 4:1, 5:1, 6:1, 7:1, 8:1, 9:1}
        for dig in numarr:
            if dig == lastdig:
                doubdig[dig] += 1
            elif dig > lastdig:
                lastdig = dig
            else:
                return False
        return hasdouble(doubdig.values())
    return False
    
def check_nums(numrange, validpw=validpw_a):
    i,maxi = list(map(int, numrange.split('-')))
    ntrue = 0
    for num in range(i,maxi+1):
        if validpw(num):
            ntrue += 1
    return ntrue

advent3 = "264793-803935"

print (validpw_a(111111))  # True
print (validpw_a(223450))  # False
print (validpw_a(123789))  # False
print ("4) answer part (a):", check_nums(advent3, validpw=validpw_a)) # 966

print (validpw_b(112233))  # True
print (validpw_b(123444))  # False
print (validpw_b(111122))  # True
print (validpw_b(111123))  # False
print (validpw_b(222344))  # True
print ("4) answer part (b):", check_nums(advent3, validpw=validpw_b)) # 628
