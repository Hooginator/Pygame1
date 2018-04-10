# -*- coding: utf-8 -*-
"""
Created on Thu Mar 29 19:40:19 2018

@author: hoog
"""

from functions import *





    
def obstacles(i):
    """ Here is the "savefile" of the walls for mazes.  """
    if(i == 0):
        return [wall(80,100,70,350),wall(150,100,300,50),wall(150,400,200,50),wall(300,250,300,50)]
    elif(i == 1):
        return [wall(200,650,1000,50),wall(200,200,50,450),wall(400,0,50,400),wall(450,350,300,50),
                wall(850,100,50,550),wall(600,100,250,50),wall(1000,0,50,500),wall(1200,200,50,500),
                wall(1250,200,200,50),wall(1400,400,200,50),wall(1250,650,200,50)]
    
def checkpoints(i):
    """ Here is the "savefile" of my checkpoints corresponding to the above maps.  """
    if(i == 0):
        return [wall(0,450,150,150),wall(50,0,150,150),wall(450,50,150,150),wall(150,200,150,150),wall(250,450,150,150)]
    elif(i == 1):
        return [wall(200,0,200,200),wall(400,400,250,250),wall(750,300,100,100),wall(450,0,200,100),wall(900,0,100,150),wall(1050,400,150,150),
        wall(1450,100,150,150),wall(1250,400,150,150),wall(1400,650,200,200),wall(0,500,200,200)]

    
############################################################
########### MAZE CLASS #####################################
############################################################

class maze:
    """ Master class for all the objects on the map that get in your way or help """
    def __init__(self,i):
        self.obstacles = obstacles(i)
        self.checkpoints = checkpoints(i)
    def drawWalls(self,screen):
        """ Create blocking visual for the list of walls given"""
        for obs in self.obstacles: obs.draw(screen)
    def drawCheckpoints(self,screen):
        """ Create small checkpointvisual for the list of walls given"""
        for obs in self.obstacles: obs.drawCheckpoint(screen)
    def drawMap(self,screen):
        """ Draw the background, walls and checkpoints."""
        screen.fill((0,0,0))
        self.drawWalls(screen)
    #drawWalls(checkpoints,screen)    
    
############################################################
########### WALL CLASS #####################################
############################################################

class obstacle():
    """ Base class for all obstacles to inherit from """
    def __init__():
        raise NotImplementedError
    def draw():
        raise NotImplementedError
    def checkCollision():
        raise NotImplementedError
     
class wall(obstacle):
    """ for impassable, rectangular walls and checkpoints"""
    def __init__(self,posx,posy,sizex,sizey):
        self.posx = posx
        self.posy = posy
        self.sizex = sizex
        self.sizey = sizey
    def draw(self,screen):
        """ Draw rectangle in the way"""
        pygame.draw.rect(screen,(0,0,255),(self.posx, self.posy, self.sizex, self.sizey))
    def drawCheckpoint(self,screen):
        """ Less intrusive draw for checkpoints"""
        pygame.draw.circle(screen,(255,255,255),self.getMidInt(), 20, 3)
    def checkCollision(self,pos):
        return ((self.posx <= pos[0]) and (self.posx + self.sizex >= pos[0]) and (self.posy <= pos[1]) and (self.posy + self.sizey >= pos[1]))
    def getMid(self):
        """ returns the center of the wall"""
        return [self.posx + self.sizex/2,self.posy + self.sizey/2]
    def getMidInt(self):
        """ returns the center of the wall AS AN INTEGER!!"""
        return [int(self.posx + self.sizex/2),int(self.posy + self.sizey/2)]

class ball(obstacle):
    """ for impassable, rectangular walls and checkpoints"""
    def __init__(self,posx,posy,width,radius):
        self.posx = posx
        self.posy = posy
        self.width = width
        self.radius = radius
    def draw(self,screen):
        """ Draw rectangle in the way"""
        pygame.draw.circle(screen,(0,0,255),(self.posx, self.posy), self.radius, self.width)
    def checkCollision(self,pos):
        dist = (pos[0]-self.posx)**2 + (pos[1]-self.posy)**2
        return dist <(self.radius)**2 and dist > (self.radius-self.width)**2
    
   
