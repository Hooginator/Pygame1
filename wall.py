# -*- coding: utf-8 -*-
"""
Created on Thu Mar 29 19:40:19 2018

@author: hoog
"""

from functions import *




def drawBackground(screen):
    """ Draws a black rectangle over the whole screen as a backdrop """
    screen.fill((0,0,0))
    
def obstacles(i):
    """ Here is the "savefile" of the walls for mazes.  """
    if(i == 0):
        return [wall(80,100,70,350),wall(150,100,300,50),wall(150,400,200,50),wall(300,250,300,50)]
    elif(i == 1):
        return [wall(200,650,1000,50),wall(200,200,50,450),wall(400,0,50,400),wall(450,350,300,50),
                wall(850,100,50,550),wall(600,100,250,50),wall(1000,0,50,500),wall(1200,200,50,500),
                wall(1250,200,200,50),wall(1400,400,200,50),wall(1250,650,200,50)]
    elif(i == 2):
        return [ball(100,300,50,0),ball(400,250,50,0),ball(700,200,50,0),ball(1000,150,50,0),ball(1300,100,50,0),
                ball(200,600,50,0),ball(500,550,50,0),ball(800,500,50,0),ball(1100,450,50,0),ball(1400,400,50,0),
                ball(300,900,50,0),ball(600,850,50,0),ball(900,800,50,0),ball(1200,750,50,0),ball(1500,700,50,0),]
    
def checkpoints(i):
    """ Here is the "savefile" of my checkpoints corresponding to the above maps.  """
    if(i == 0):
        return [wall(0,450,150,150),wall(50,0,150,150),wall(450,50,150,150),wall(150,200,150,150),wall(250,450,150,150)]
    elif(i == 1):
        return [wall(200,0,200,200),wall(400,400,250,250),wall(750,300,100,100),wall(450,0,200,100),wall(900,0,100,150),wall(1050,400,150,150),
        wall(1450,100,150,150),wall(1250,400,150,150),wall(1400,650,200,200),wall(0,500,200,200)]
    elif(i == 2):
        return [ball(500,800,60,0),ball(300,100,60,0),ball(1300,600,60,0),ball(200,800,60,0)]    

def fuelParams(i):
    fp = {0 : [50,200,0.7],
          1 : [50,200,0.7],
          2 : [300,300,0.7],
          }
    return fp[i]

    
############################################################
########### MAZE CLASS #####################################
############################################################

class maze:
    """ Master class for all the objects on the map that get in your way or help """
    def __init__(self,i = 1,height = 900,width = 1600):
        self.obstacles = obstacles(i)
        self.checkpoints = checkpoints(i)
        self.chechpointsPerLap = len(self.checkpoints)
        self.screenWidth, self.screenHeight = width, height
        self.getFuelCosts(i)
        if(i > 2):
            self.mazeType = "circular"
        else:
            self.mazeType = "linear"
    def getFuelCosts(self,mazeNumber):
        self.fuelParams = fuelParams(mazeNumber)
    def checkFuelCost(self, currentLap,currentCheckpoint):
        """ Claculates the amount of time in frames a ship gets to make a checkpoint """
        return  self.fuelParams[0] + self.fuelParams[1]*(currentLap * len(self.checkpoints) + currentCheckpoint )** self.fuelParams[2]
    def drawWalls(self,screen):
        """ Create blocking visual for the list of walls given"""
        for obs in self.obstacles: obs.draw(screen)
    def drawCheckpoints(self,screen):
        """ Create small checkpointvisual for the list of walls given"""
        for obs in self.obstacles: obs.drawCheckpoint(screen)
    def drawMap(self,screen):
        """ Draw the background, walls and checkpoints."""
        drawBackground(screen)
        self.drawWalls(screen)
    #drawWalls(checkpoints,screen)    
    def checkCollisions(self,pos):
        """ Checks pos (x,y) against all walls for collision"""
        for obs in self.obstacles:
            if(obs.checkCollision(pos)): return True
        if((pos[0] < 0) or (pos[0] > self.screenWidth) or (pos[1] < 0) or (pos[1] > self.screenHeight)): return True
        return False
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
    def __init__(self,posx,posy,radius,width):
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
    def getMid(self):
        """ returns the center of the wall"""
        return [self.posx,self.posy]

    
   
