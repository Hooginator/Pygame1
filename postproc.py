#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec  1 17:05:40 2018

@author: hoog
"""

import numpy as np
import matplotlib.pyplot as plt

def readTopScores(filename):
    """ This will read and return the topscores file generated with each race for plotting
    """
    raw  = []
    
    with open("./data/"+filename+"/topscores","r") as f: 
        print(filename)
        for line in f:
            raw.append([float(i) for i in line.strip("\n").strip(" ").split(" ")])
    return raw        

#plotTopScores("INPUTANG04DIS50_1x1")
            
mydata = []
for i in range(200):
    fname = "DEC8_10ships_noevolutionatall_"+str(i+1) 
    temp = readTopScores(fname)
    mydata.append(temp)
    
    plt.plot(temp)
plt.show()