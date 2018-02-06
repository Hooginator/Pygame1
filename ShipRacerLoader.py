# -*- coding: utf-8 -*-
"""
Created on Tue Feb  6 14:46:24 2018

@author: hoog
"""
import numpy as np

def loadShip(filename):
    return np.load(filename)
    
abc = loadShip("./data/BestShips_W1_G0.npy")
print(str(abc))
defg = loadShip("./data/BestShips_W1_G1.npy")
print(str(defg))

print (str(abc - defg))