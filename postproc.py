#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec  1 17:05:40 2018

@author: hoog
"""

def plotTopScores(filename):
    with open("./data/"+filename+"/topscores","r") as f: 
        for line in f:
            print(line)
            
            
#plotTopScores("INPUTANG04DIS50_1x1")
            
abc = ["hello"]

for a in abc:
    print("here")