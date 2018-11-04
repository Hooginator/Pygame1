#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 30 21:04:43 2018

@author: hoog
"""



def mapArrayFromStr(wallPos):
    """ Takes a string of 1 or 0 corresponding to where walls are with new
    lines separated by \n"""
    wallArray = []
    i = 0 # 'i' counts the current line of the file we are on
    for line in wallPos.split('\n'):
        print(len(line))
        wallArray.append([line[0]])
        j = 1 # 'j' counts the current character we are on in line 'i'
        while j < len(line):
            wallArray[i].append(line[j])
            j+=1
        i+=1
    return wallArray    
        
def mapStrFromFile(filename):
    pass
    
abc = mapArrayFromStr("111010\n010101010\n0101010101\n01010101010101")
print(abc)