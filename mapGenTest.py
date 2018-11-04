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
        if(len(line) !=0):
            wallArray.append([line[0]])
        j = 1 # 'j' counts the current character we are on in line 'i'
        while j < len(line):
            wallArray[i].append(line[j])
            j+=1
        i+=1
    return wallArray    
        
def mapStrFromFile(filename):
    """ Reads the file given as a string for further processing """
    with open(filename, 'r') as myfile:
        data = myfile.read()
    return data
    
cab = mapStrFromFile("Map1_wall.txt")
abc = mapArrayFromStr(cab)





def generateMapStr(XMAX,YMAX,minWidth=3):
    """ Will build a map of size [XMAX,YMAX] with a path throughout a minimum 
    of minWidth wide. I don't really know how to do this yet. manual for now"""