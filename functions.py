# -*- coding: utf-8 -*-
"""
Created on Thu Mar 22 21:58:56 2018

@author: hoog
"""

import sys, pygame
import numpy as np
import copy
import os

pygame.init()
pygame.display.init()

myfont = pygame.font.SysFont('Comic Sans MS', 30)

############################################################
########### FUNCTIONS ######################################
############################################################



def checkCollisions(walls,pos,width,height):
    """ Checks pos (x,y) against all walls for collision"""
    for wall in walls:
        if(wall.checkCollision(pos[0],pos[1])): return True
    if((pos[0] < 0) or (pos[0] > width) or (pos[1] < 0) or (pos[1] > height)): return True
    return False
def drawWalls(walls):
    """ Create blocking visual for the list of walls given"""
    for wall in walls: wall.drawWall()
def drawCheckpoints(walls):
    """ Create small checkpointvisual for the list of walls given"""
    for wall in walls: wall.drawCheckpoint()
def getDist(pos1,pos2):
    """ returns the pythagorean distance between 2 vectors"""
    return np.sqrt((pos1[0]-pos2[0])*(pos1[0]-pos2[0])+(pos1[1]-pos2[1])*(pos1[1]-pos2[1]))
def logis(a): 
    """ "Logistic function" """
    b = 1/(1+np.exp(a))
    return b
def checkFuelCost(CHPTS, LAPS,checkpointPerLap):
    return  50 + 200*(LAPS * checkpointPerLap + CHPTS )** 0.7
    
    