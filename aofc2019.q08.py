# python3

# 8)

import os

def image_info(file, r, c):
    lsize = r * c
    image = os.popen("cat "+file).read().strip()
    nlayers = int(len(image) / lsize)
    return image, nlayers, lsize
    
def advent8a(file, r, c):
    image, nlayers, lsize = image_info(file, r, c)
    zfewest = float("inf")
    zlayer = []
    start = 0
    for l in range(1,nlayers+1):
        layer = image[start:l*lsize]
        zcount = layer.count("0")
        if zcount < zfewest:
            zfewest = zcount
            zlayer = layer
        start = l*lsize

    nos = list(map(int, list(zlayer)))
    ones = nos.count(1)
    twos = nos.count(2)
    print (ones * twos)

def make2D(a, r, c):
    start = 0
    a2D = []
    for row in range(1,r+1):
        suba = a[start:row*c]
        a2D.append(suba)
        start = row*c
    return a2D

# return 3D array: layers[depth][row][col]
def get_layers(file, r, c):
    image, nlayers, lsize = image_info(file, r, c)
    start = 0
    layers = []
    for l in range(1,nlayers+1):
        layer = image[start:l*lsize]
        layer2D = make2D(list(map(int, list(layer))), r, c)
        layers.append(layer2D)
        start = l*lsize
    return layers

def advent8b(file, r, c):
    layers = get_layers(file, r, c)  # layers[depth][row][col]
    pic = [[0 for col in range(c)] for row in range (r)]
    for row in range(r):
        for col in range(c):
            for depth in range(len(layers)):
                pix = layers[depth][row][col]
                if pix == 2:
                    continue
                elif pix == 1:
                    pic[row][col] = 1
                    break
                elif pix == 0:
                    pic[row][col] = 0
                    break
    for row in pic:
        print (row)


advent8a_file = "advent8a.txt"
advent8a(advent8a_file, 6, 25)  # 1340

advent8b(advent8a_file, 6, 25)  # LEJKC
