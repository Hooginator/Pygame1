# -*- coding: utf-8 -*-
"""
Created on Thu Mar 29 19:40:19 2018

@author: hoog
"""

from functions import *


def rotate(pos,angle):
    return(pos[0]*np.cos(angle)- pos[1]*np.sin(angle),
           pos[0]*np.sin(angle)+ pos[1]*np.cos(angle))

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
                wall((1250,200),(200,50)),wall((1400,400),(200,50)),wall((1250,650),(200,50)),rotatingRect((300,300),(20,200),)]
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
    fp = {0 : [200,0.7],
          1 : [200,0.7],
          2 : [500,0.9],
          3 : [500,0.9],
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
        self.checkpointsPerLap = len(self.checkpoints)
        self.screenWidth, self.screenHeight = width, height
        self.getFuelCosts(i)
        if(i > 2):
            self.mazeType = "linear"
        else:
            self.mazeType = "circular"
    def getFuelCosts(self,mazeNumber):
        self.fuelParams = fuelParams(mazeNumber)
    def checkFuelCost(self, currentCheckpoint, currentLap = None):
        """ Claculates the amount of time in frames a ship gets to make a checkpoint """
        if(currentLap == None): 
            currentLap = currentCheckpoint //  self.checkpointsPerLap
            currentCheckpoint = currentCheckpoint % self.checkpointsPerLap
        return  self.fuelParams[0]*(currentLap * len(self.checkpoints)+ 1 + currentCheckpoint )** self.fuelParams[1]
    def drawWalls(self,screen):
        """ Create blocking visual for the list of walls given"""
        for obs in self.obstacles: obs.draw(screen)
    def drawCheckpoints(self,screen,frame):
        """ Create small checkpointvisual for the list of walls given"""
        for chp in self.checkpoints: chp.drawCheckpoint(screen,frame)
    def drawCheckpoint(self,screen,i,frame):
        self.checkpoints[i%len(self.checkpoints)].drawCheckpoint(screen,frame)
    def drawMap(self,screen):
        """ Draw the background, walls and checkpoints."""
        drawBackground(screen)
        for obs in self.obstacles:
            obs.update()
        self.drawWalls(screen)
    #drawWalls(checkpoints,screen)   
    def newGeneration(self):
        for obs in self.obstacles: obs.restart()
    def checkCollisions(self,pos,size = 0):
        """ Checks pos (x,y) against all walls for collision"""
        for obs in self.obstacles:
            if(obs.checkCollision(pos,size)): return True
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
        """ Returns true on collision """
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
        pygame.draw.rect(screen,(0,0,240),(self.pos[0], self.pos[1], self.size[0], self.size[1]))
    def drawCheckpoint(self,screen,frame):
        """ Less intrusive draw for checkpoints"""
        pygame.draw.circle(screen,[max(0,tmp - (20 - frame%20)*10) for tmp in (240,240,240)],
                                   self.getMidInt(), 1 + frame %20, 1)
        pygame.draw.circle(screen,(240,240,240),self.getMidInt(), 21 + frame %20, 1)
        pygame.draw.circle(screen,[max(0,tmp - (frame%20)*10) for tmp in (240,240,240)],
                                   self.getMidInt(), 41 + frame %20, 1)
    def checkCollision(self,pos,size = 0):
        """ Returns true on collision """
        return ((self.pos[0]+ size <= pos[0]) and (self.pos[0] + size + self.size[0] >= pos[0]) 
                and (self.pos[1] + size <= pos[1]) and (self.pos[1] + size + self.size[1] >= pos[1]))
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
        pygame.draw.circle(screen,(0,0,240),self.pos, self.radius, self.width)
    def checkCollision(self,pos,size = 0):
        """ Returns true on collision """
        dist = (pos[0]-self.pos[0])**2 + (pos[1]-self.pos[1])**2
        if(self.width == 0):
            return dist - size <(self.radius)**2
        else:
            return dist - size <(self.radius)**2 and dist + size > (self.radius-self.width)**2 
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
        pygame.draw.circle(screen,(0,0,240),self.pos, self.radius, self.width)
    def checkCollision(self,pos,size = 0):
        """ Returns true on collision """
        dist = (pos[0]-self.pos[0])**2 + (pos[1]-self.pos[1])**2
        if(self.width == 0):
            return dist - size <(self.radius)**2
        else:
            return dist - size <(self.radius)**2 and dist + size > (self.radius-self.width)**2 
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
        
class rotatingRect(obstacle):
    def __init__(self,midPos,rectSize,vel = 0.01,startAngle = 0.5):
        self.midPos = midPos
        self.size = rectSize
        self.angle = startAngle
        self.vel = vel
        self.basePoint = ((-0.5*self.size[0],-0.5*self.size[1]),
                          (0.5*self.size[0],-0.5*self.size[1]),
                          (0.5*self.size[0],0.5*self.size[1]),
                          (-0.5*self.size[0],0.5*self.size[1]))
        
    def draw(self,screen):
        pygame.draw.polygon(screen,(0,0,240),self.pointList)
    def update(self):
        self.angle += self.vel
        self.updatePointList()
    def updatePointList(self):
        self.pointList = []
        for bp in self.basePoint:
            temppoint = rotate(bp,self.angle)
            self.pointList.append((self.midPos[0] +temppoint[0]
                            ,self.midPos[1] +temppoint[1]))
        

    def checkCollision(self,pos,size = 0):
        temp = (pos[0] - self.midPos[0], pos[1] - self.midPos[1])
        temp = rotate(temp,-1*self.angle)     
        return ((-0.5*self.size[0]- size <= temp[0]) and (0.5*self.size[0] + size + self.size[0] >= temp[0]) 
                and (-0.5*self.size[1] - size <= temp[1]) and (0.5*self.size[1] + size + self.size[1] >= temp[1]))
    
        return False
        
   
