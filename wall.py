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
        return [wall((80,100),(70,350)),wall((150,100),(300,50)),wall((150,400),(200,50)),wall((300,250),(300,50))]
    elif(i == 1):
        return [wall((200,650),(1000,50)),wall((200,200),(50,450)),wall((400,0),(50,400)),wall((450,350),(300,50)),
                wall((850,100),(50,550)),wall((600,100),(250,50)),wall((1000,0),(50,500)),wall((1200,200),(50,500)),
                wall((1250,200),(200,50)),wall((1400,400),(200,50)),wall((1250,650),(200,50))]
    elif(i == 2):
        return [ball((100,300),50,0),ball((400,250),50,0),ball((700,200),50,0),ball((1000,150),50,0),ball((1300,100),50,0),
                ball((200,600),50,0),ball((500,550),50,0),ball((800,500),50,0),ball((1100,450),50,0),ball((1400,400),50,0),
                ball((300,900),50,0),ball((600,850),50,0),ball((900,800),50,0),ball((1200,750),50,0),ball((1500,700),50,0),]
    elif(i == 3):
        return [movingBall((300,300),50,0),movingBall((600,300),50,0),movingBall((900,300),50,0),movingBall((1200,300),50,0),
                movingBall((300,600),50,0),movingBall((600,600),50,0),movingBall((900,600),50,0),movingBall((1200,600),50,0),
                movingBall((300,900),50,0),movingBall((600,900),50,0),movingBall((900,900),50,0),movingBall((1200,900),50,0),]
def checkpoints(i):
    """ Here is the "savefile" of my checkpoints corresponding to the above maps.  """
    if(i == 0):
        return [wall((0,450),(150,150)),wall((50,0),(150,150)),wall((450,50),(150,150)),wall((150,200),(150,150)),wall((250,450),(150,150))]
    elif(i == 1):
        return [wall((200,0),(200,200)),wall((400,400),(250,250)),wall((750,300),(100,100)),wall((450,0),(200,100)),wall((900,0),(100,150)),wall((1050,400),(150,150)),
        wall((1450,100),(150,150)),wall((1250,400),(150,150)),wall((1400,650),(200,200)),wall((0,500),(200,200))]
    elif(i == 2):
        return [ball((500,800),60,0),ball((300,100),60,0),ball((1300,600),60,0),ball((200,800),60,0)]    
    elif(i == 3):
        return [ball((500,800),60,0),ball((300,100),60,0),ball((1300,600),60,0),ball((200,800),60,0)]    

def fuelParams(i):
    fp = {0 : [50,200,0.7],
          1 : [50,200,0.7],
          2 : [300,300,0.7],
          3 : [300,300,0.7],
          }
    return fp[i]

    
############################################################
########### MAZE CLASS #####################################
############################################################

class maze:
    """ Master class for all the objects on the map that get in your way or help """
    def __init__(self,i = 3,height = 900,width = 1600):
        self.obstacles = obstacles(i)
        self.checkpoints = checkpoints(i)
        self.checkpointsPerLap = len(self.checkpoints)
        self.screenWidth, self.screenHeight = width, height
        self.getFuelCosts(i)
        if(i > 2):
            self.mazeType = "circular"
        else:
            self.mazeType = "linear"
    def getFuelCosts(self,mazeNumber):
        self.fuelParams = fuelParams(mazeNumber)
    def checkFuelCost(self, currentCheckpoint, currentLap = None):
        """ Claculates the amount of time in frames a ship gets to make a checkpoint """
        if(currentLap == None): 
            currentLap = currentCheckpoint //  self.checkpointsPerLap
            currentCheckpoint = currentCheckpoint % self.checkpointsPerLap
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
        for obs in self.obstacles:
            obs.update()
        self.drawWalls(screen)
    #drawWalls(checkpoints,screen)   
    def newGeneration(self):
        for obs in self.obstacles: obs.restart()
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
    def __init__(self):
        raise NotImplementedError
    def draw(self):
        raise NotImplementedError
    def checkCollision(self):
        raise NotImplementedError
    def update(self):
        pass
    def restart(self):
        pass
     
class wall(obstacle):
    """ for impassable, rectangular walls and checkpoints"""
    def __init__(self,pos,size):
        self.pos = pos
        self.size = size
    def draw(self,screen):
        """ Draw rectangle in the way"""
        pygame.draw.rect(screen,(0,0,255),(self.pos[0], self.pos[1], self.size[0], self.size[1]))
    def drawCheckpoint(self,screen):
        """ Less intrusive draw for checkpoints"""
        pygame.draw.circle(screen,(255,255,255),self.getMidInt(), 20, 3)
    def checkCollision(self,pos):
        return ((self.pos[0] <= pos[0]) and (self.pos[0] + self.size[0] >= pos[0]) 
                and (self.pos[1] <= pos[1]) and (self.pos[1] + self.size[1] >= pos[1]))
    def getMid(self):
        """ returns the center of the wall"""
        return [self.pos[0] + self.size[0]/2,self.pos[1] + self.size[1]/2]
    def getMidInt(self):
        """ returns the center of the wall AS AN INTEGER!!"""
        return [int(self.pos[0] + self.size[0]/2),int(self.pos[1] + self.size[1]/2)]

class ball(obstacle):
    """ for impassable, rectangular walls and checkpoints"""
    def __init__(self,pos,radius,width):
        self.pos = pos
        self.width = width
        self.radius = radius
    def draw(self,screen):
        """ Draw rectangle in the way"""
        pygame.draw.circle(screen,(0,0,255),self.pos, self.radius, self.width)
    def checkCollision(self,pos):
        dist = (pos[0]-self.pos[0])**2 + (pos[1]-self.pos[1])**2
        return dist <(self.radius)**2 and dist > (self.radius-self.width)**2
    def getMid(self):
        """ returns the center of the wall"""
        return self.pos

class movingBall(obstacle):
    def __init__(self,pos,radius,width,vel = None,xlims = (0,1600), ylims = (0,900)):
        self.pos = list(map(int,pos))
        self.startpos = list(map(int,pos))
        self.width = int(width)
        self.radius = int(radius)    
        self.xlims, self.ylims = xlims, ylims
        
        if(vel == None):
            self.vel = np.random.randint(-10,10,2)
        else: 
            self.vel = vel
    def draw(self,screen):
        """ Draw rectangle in the way"""
        pygame.draw.circle(screen,(0,0,255),self.pos, self.radius, self.width)
    def checkCollision(self,pos):
        dist = (pos[0]-self.pos[0])**2 + (pos[1]-self.pos[1])**2
        if(self.width == 0):
            return dist <(self.radius)**2
        else:
            return dist <(self.radius)**2 and dist > (self.radius-self.width)**2 
    def update(self):
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        if(self.pos[0] < self.xlims[0] - self.radius or self.pos[0] > self.xlims[1] + self.radius ): 
            self.vel[0] = -1*self.vel[0] 
        if(self.pos[1] < self.ylims[0] - self.radius or self.pos[1] > self.ylims[1] + self.radius ): 
            self.vel[1] = -1*self.vel[1] 
    def restart(self):
        self.pos[0] = self.startpos[0]
        self.pos[1] = self.startpos[1]
        
        
   
