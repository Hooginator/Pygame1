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



def getDist(pos1, pos2):
    """ returns the pythagorean distance between 2 vectors"""
    return np.sqrt((pos1[0]-pos2[0])*(pos1[0]-pos2[0])+(pos1[1]-pos2[1])*(pos1[1]-pos2[1]))

def logis(a): 
    """ "Logistic function" """
    b = 1/(1+np.exp(-1*a))
    return b

def getOffsetPos(pos,midpos,height = 900,width  = 1600):
    """ Takes the position relative to (0,0) in the top left corner and 
    changes it to be in a frame where midpos is in the middle used for having
    the camera follow a ship by moving everything around it
    """
    
    return (int(pos[0] - (midpos[0]-width/2)), int(pos[1] - (midpos[1]-height/2)))
    

def drawRadiatingCircle(screen, 
    middle, # Position for the middle of the circle to be drawn
    frame, # frame number is how we track the growing of the circle
    colour = (240,240,240), 
    number = 3, 
    size = 60, # This is the maximum size, if it's easier in the math to make this a bit smaller I will
    cycle_length = 30 # number of frames for pattern to repeat
    ):
    """ Draws circles that grow and dissapear for indicating a position """
    
    size_per_circle = size//number
    colour_per_frame = max(colour)//cycle_length
    
    
    # Build a temporary screen, for the alpha to work we CANNOT BUILD BLACK (0,0,0) CIRCLES FOR NOW
    
    
    if number > 1:
        for n in range(number):
            temp_alpha = 255
            temp_screen = pygame.Surface((size*2,size*2))
            temp_screen.set_colorkey((0,0,0))
            if n == 0:
                # brightening phase
                temp_alpha = (frame%(cycle_length))*255/(cycle_length)
                #temp_colour = tuple(max(0,tmp - (cycle_length - frame%cycle_length)*colour_per_frame) for tmp in colour)
            elif n ==  number -1:
                # fading Phase
                temp_alpha = (cycle_length - frame%(cycle_length))*255/(cycle_length)
                #temp_colour = tuple(max(0,tmp - (frame%cycle_length)*colour_per_frame) for tmp in colour)   
            temp_size = int(1 + (frame %(cycle_length))/(cycle_length)*size_per_circle + n*size_per_circle)
            
            # Draw the circle onto the temp screen and blit that screen onto the main screen for alpha to work
            pygame.draw.circle(temp_screen,colour,(size,size),temp_size,1)
            temp_screen.set_alpha(temp_alpha)
    
            screen.blit(temp_screen,(middle[0] - size,middle[1] - size))
            
            
    # elif number == 1: # dont
        # if frame % cycle_length < cycle_length/2:
            # temp_colour = tuple(max(0,tmp - (cycle_length - frame%cycle_length)*colour_per_frame) for tmp in colour)
        # else:
            # temp_colour = tuple(max(0,tmp - (frame%cycle_length)*colour_per_frame) for tmp in colour) 
        # pygame.draw.circle(screen,temp_colour, middle,  1 + frame %cycle_length, 1)
        
        
def drawPulsatingCirlce(screen, 
    middle, # Position for the middle of the circle to be drawn
    frame, # frame number is how we track the growing of the circle
    magnitude = 1, # How bright base don input of length
    colour = (240,240,240), 
    size = 10, 
    cycle_length = 60,
    pulsating_strength = 0.8,
    reverse_alpha = False):
    
    # Build a temporary screen, for the alpha to work we CANNOT BUILD BLACK (0,0,0) CIRCLES FOR NOW
    temp_screen = pygame.Surface((size*2,size*2))
    temp_screen.set_colorkey((0,0,0))

    # Separate the animation into the growing and shrinking parts
    if frame% cycle_length >= cycle_length/2:
        # growing phase
        temp_alpha = ((cycle_length/2 - frame%(cycle_length/2)*pulsating_strength+1-pulsating_strength)*255/(cycle_length/2))
        temp_size = int(1 + (frame %(cycle_length/2))/(cycle_length/2)*size)
    else:
        # Shrinking Phase
        temp_alpha = ((frame%(cycle_length/2)*pulsating_strength+1-pulsating_strength)*255/(cycle_length/2))
        temp_size = int(1 + (cycle_length/2 - frame %(cycle_length/2))/(cycle_length/2)*size)
    if reverse_alpha:
        temp_alpha = 255 - temp_alpha
    temp_alpha = temp_alpha*magnitude
    # Draw the circle onto the temp screen and blit that screen onto the main screen for alpha to work
    pygame.draw.circle(temp_screen,colour,(size,size),temp_size,1)
    temp_screen.set_alpha(temp_alpha)
    
    screen.blit(temp_screen,(middle[0] - size,middle[1] - size))
    
    #pygame.draw.circle(screen,temp_colour, middle,  temp_size, 1)
        
