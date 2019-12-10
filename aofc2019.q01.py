# python3

# 1)

import os

def calc_fuel(mass):
    return int(mass/3) - 2

def calc_recursive_fuel(mass):
    fuel = calc_fuel(mass)
    tfuel = fuel
    while tfuel >= 0:
        tfuel = calc_fuel(tfuel)
        if tfuel > 0:
            fuel += tfuel
    return fuel

def calc_advent1a(file):
    total_fuel = 0
    for line in os.popen("cat "+file).read().splitlines():
        total_fuel += calc_fuel(int(line))
    return total_fuel

def calc_advent1b(file):
    total_fuel = 0
    for line in os.popen("cat "+file).read().splitlines():
        total_fuel += calc_recursive_fuel(int(line))
    return total_fuel

advent1a_file = "advent1a.txt"
advent1b_file = "advent1a.txt"  # use same file

# Egs part (1a).
print (calc_fuel(12))       # 2
print (calc_fuel(14))       # 2
print (calc_fuel(1969))     # 654
print (calc_fuel(100756))   # 33583
print ("1) answer to part (a):",calc_advent1a(advent1a_file)) # 3198599

# Egs for part (1b)
print (calc_recursive_fuel(12))       # 2
print (calc_recursive_fuel(14))       # 2
print (calc_recursive_fuel(1969))     # 966
print (calc_recursive_fuel(100756))   # 50346
print ("1) answer to part (b):",calc_advent1b(advent1b_file)) # 4795042
