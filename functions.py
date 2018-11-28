# -*- coding: utf-8 -*-
"""
Created on Thu Mar 22 21:58:56 2018

@author: hoog
"""

import sys, pygame
import numpy as np
import copy
import os
import time
import pickle

pygame.init()
pygame.display.init()

myfont = pygame.font.SysFont('arial', 24)

############################################################
########### FUNCTIONS ######################################
############################################################



def getDist(pos1,pos2):
    """ returns the pythagorean distance between 2 vectors"""
    return np.sqrt((pos1[0]-pos2[0])*(pos1[0]-pos2[0])+(pos1[1]-pos2[1])*(pos1[1]-pos2[1]))

def logis(a): 
    """ "Logistic function" """
    b = 1/(1+np.exp(-1*a))
    return b

def getOffsetPos(pos,midpos,height = 900,width  = 1600):
    """ Takes the position relative to (0,0) in the top left corner and 
    changes it to be in a frame where midpos is in the middle used for having
    the camera follow a ship by moving everything around it"""
    
    return (int(pos[0] - (midpos[0]-width/2)), int(pos[1] - (midpos[1]-height/2)))