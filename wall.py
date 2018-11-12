# -*- coding: utf-8 -*-
"""
Created on Thu Mar 29 19:40:19 2018

@author: hoog
"""

MIN_WALL_SIZE = 50

from functions import *

############################################################
########### LOADING ########################################
############################################################
def mapArrayFromStr(wallPos):
    """ Takes a string of 1 or 0 corresponding to where walls are with new
    lines separated by \n"""
    wallArray = []
    i = 0 # 'i' counts the current line of the file we are on
    for line in wallPos.split('\n'):
        if(len(line) !=0):
            wallArray.append([int(line[0])])
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

def generateObstacles(filename):
    mapArray = mapArrayFromStr(mapStrFromFile(filename+"_wall.txt"))
    obstacles = []
    checkpoints = [None]*9
    i = 0
    for mapRow in mapArray:
        for j, w in enumerate(mapRow):
            if(int(w) == 1):
                obstacles.append(wall(layoutToPos((j,i)),(MIN_WALL_SIZE,MIN_WALL_SIZE)))
            if(int(w) > 1):
                checkpoints[int(w)-2] = (wall(layoutToPos((j-1,i-1)),
                            (3*MIN_WALL_SIZE,3*MIN_WALL_SIZE)))
                
        i+=1
    while(checkpoints[-1] == None): del(checkpoints[-1])
    return mapArray, obstacles, checkpoints
        

def layoutToPos(lpos):
    """ Returns the center position associated with the grid spot x, y """
    return (lpos[0]*MIN_WALL_SIZE,lpos[1]*MIN_WALL_SIZE)
def posToLayout(pos):
    """ Returns the spot in self.layout that pos would fall in.  For collision check"""
    return (int(pos[0]/50),int(pos[1]/50))
    

def rotate(pos,angle):
    return(pos[0]*np.cos(angle)- pos[1]*np.sin(angle),
           pos[0]*np.sin(angle)+ pos[1]*np.cos(angle))

def drawBackground(screen):
    """ Draws a black rectangle over the whole screen as a backdrop """
    screen.fill((0,0,0))
 # Hopefully obsolete   
#def obstacles(i):
#    """ Here is the "savefile" of the walls for mazes.  """
#    if(i == 0):
#        return [wall((80,100),(70,350)),wall((150,100),(300,50)),wall((150,400),(200,50)),wall((300,250),(300,50))]
#    elif(i == 1):
#        return [wall((200,650),(1000,50)),wall((200,200),(50,450)),wall((400,0),(50,400)),wall((450,350),(300,50)),
#                wall((850,100),(50,550)),wall((600,100),(250,50)),wall((1000,0),(50,500)),wall((1200,200),(50,500)),
#                wall((1250,200),(200,50)),wall((1400,400),(200,50)),wall((1250,650),(200,50))]
#    elif(i == 2):
#        return [ball((100,300),50,0),ball((400,250),50,0),ball((700,200),50,0),ball((1000,150),50,0),ball((1300,100),50,0),
#                ball((200,600),50,0),ball((500,550),50,0),ball((800,500),50,0),ball((1100,450),50,0),ball((1400,400),50,0),
#                ball((300,900),50,0),ball((600,850),50,0),ball((900,800),50,0),ball((1200,750),50,0),ball((1500,700),50,0),]
#    elif(i == 3):
#        return [movingBall((300,300),50,0),movingBall((600,300),50,0),movingBall((900,300),50,0),movingBall((1200,300),50,0),
#                movingBall((300,600),50,0),movingBall((600,600),50,0),movingBall((900,600),50,0),movingBall((1200,600),50,0),
#                movingBall((300,900),50,0),movingBall((600,900),50,0),movingBall((900,900),50,0),movingBall((1200,900),50,0),]
#def checkpoints(i):
#    """ Here is the "savefile" of my checkpoints corresponding to the above maps.  """
#    if(i == 0):
#        return [wall((0,450),(150,150)),wall((50,0),(150,150)),wall((450,50),(150,150)),wall((150,200),(150,150)),wall((250,450),(150,150))]
#    elif(i == 1):
#        return [wall((200,0),(200,200)),wall((400,400),(250,250)),wall((750,300),(100,100)),wall((450,0),(200,100)),wall((900,0),(100,150)),wall((1050,400),(150,150)),
#        wall((1450,100),(150,150)),wall((1250,400),(150,150)),wall((1400,650),(200,200)),wall((0,500),(200,200))]
#    elif(i == 2):
#        return [ball((500,800),60,0),ball((300,100),60,0),ball((1300,600),60,0),ball((200,800),60,0)]    
#    elif(i == 3):
#        return [ball((500,800),60,0),ball((300,100),60,0),ball((1300,600),60,0),ball((200,800),60,0)]    

def fuelParams(i):
    fp = {0 : [200,0.7],
          1 : [400,0.7],
          2 : [500,0.9],
          3 : [500,0.9],
          }
    return fp[i]

    
############################################################
########### MAZE CLASS #####################################
############################################################

class maze:
    """ Master class for all the objects on the map that get in your way or 
    help """
    def __init__(self,mapName = "Map1",height = 900,width = 1600,i = 1):
        # Load the wall and checkpoint information
        self.layout, self.obstacles, self.checkpoints = generateObstacles(mapName)
        self.checkpointsPerLap = len(self.checkpoints)
        self.screenWidth, self.screenHeight = width, height
        self.layoutHeight, self.layoutWidth = len(self.layout[:]),len(self.layout[0][:])
        #self.addBoundaryWall()
        self.getFuelCosts(i)
        if(i > 2):
            self.mazeType = "linear"
        else:
            self.mazeType = "circular"
            
    def getFuelCosts(self,mazeNumber):
        self.fuelParams = fuelParams(mazeNumber)
        
    def getCheckpointPos(self,n):
        return self.checkpoints[n].getMidInt()
        
    def checkFuelCost(self, currentCheckpoint, currentLap = None):
        """ Claculates the amount of time in frames a ship gets to make a 
        checkpoint """
        if(currentLap == None): 
            currentLap = currentCheckpoint //  self.checkpointsPerLap
            currentCheckpoint = currentCheckpoint % self.checkpointsPerLap
        return  self.fuelParams[0]*(currentLap * len(self.checkpoints)+ 1 
                               + currentCheckpoint )** self.fuelParams[1]
        
        
    def drawWalls(self,screen,midpos = (450,800),zoom = 1):
        """ Create blocking visual for the list of walls given"""
        for obs in self.obstacles: obs.draw(screen,midpos = midpos)
    def addBoundaryWall(self):
        self.obstacles.append(wall((-50,-50),(self.screenWidth + 100,50)))
        self.obstacles.append(wall((-50,self.screenHeight),(self.screenWidth + 100,50)))
        self.obstacles.append(wall((-50,0),(50,self.screenHeight + 50)))
        self.obstacles.append(wall((self.screenWidth,0),(50,self.screenHeight + 50)))
        
    def drawCheckpoints(self,screen,frame,midpos):
        """ Create small checkpointvisual for the list of walls given"""
        for chp in self.checkpoints: chp.drawCheckpoint(screen,frame,midpos)
    
    def drawCheckpoint(self,screen,i,frame,midpos):
        self.checkpoints[i%len(self.checkpoints)].drawCheckpoint(screen,frame,midpos = midpos)
    
    def drawMap(self,screen,midpos = None, followLead = False):
        """ Draw the background, walls and checkpoints."""
        
        if midpos is None or followLead is False: 
            midpos = (800,450)
        drawBackground(screen)
        self.drawWalls(screen,midpos = midpos)
    #drawWalls(checkpoints,screen)   
    def updateMap(self):
        """ Updates all objects in the obstacles """
        for obs in self.obstacles:
            obs.update()
        
    def newGeneration(self):
        for obs in self.obstacles: obs.restart()
    
    def isInBoundaries(self,pos):
        if(pos[0] > 0 and pos[0] < MIN_WALL_SIZE*self.layoutWidth and 
           pos[1] > 0 and pos[1] < MIN_WALL_SIZE*self.layoutHeight):
            return True
        else: return False
    
    def checkLayoutCollisions(self,pos,size=0):
        if(self.isInBoundaries(pos)):
            temppos = posToLayout(pos)
            if(int(self.layout[temppos[1]][temppos[0]]) == 1): 
                return 1
            else: return 0
        else: return 1
    
    def checkCollisions(self,pos,size = 0):
        """ Checks pos (x,y) against all walls for collision"""
        tempint = self.checkLayoutCollisions(pos)
        #print(tempint)
        if(tempint == 1): return True
        return False
        # Old check for collisions
        #for obs in self.obstacles:
        #    if(obs.checkCollision(pos,size)): return True
        #if((pos[0] < 0) or (pos[0] > self.screenWidth) or (pos[1] < 0) 
        #    or (pos[1] > self.screenHeight)): return True
        #return False
############################################################
########### WALL CLASS #####################################
############################################################

class obstacle():
    """ Base class for all obstacles to inherit from containing some universal
    functions and a few that need to be overwritten for any obstacle."""
    def __init__(self):
        raise NotImplementedError
    def getMidInt(self):
        raise NotImplementedError
    def draw(self):
        raise NotImplementedError
    def drawCheckpoint(self,screen,frame,midpos = (800,450)):
        """ Draws the checkpoint indicator in the middle of the selected object
        Usually for showing where time is about to expire"""       
        
        temppos = getOffsetPos(self.getMidInt(),midpos)
        pygame.draw.circle(screen,[max(0,tmp - (20 - frame%20)*10) for tmp in (240,240,240)],
                                   temppos, 1 + frame %20, 1)
        pygame.draw.circle(screen,(240,240,240),temppos, 21 + frame %20, 1)
        pygame.draw.circle(screen,[max(0,tmp - (frame%20)*10) for tmp in (240,240,240)],
                                   temppos, 41 + frame %20, 1)
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
        
    def draw(self,screen,midpos = (450,800)):
        """ Draw rectangle in the way"""
        temppos = getOffsetPos(self.pos,midpos)
        pygame.draw.rect(screen,(0,0,240),(temppos[0], temppos[1], self.size[0], self.size[1]))
    
    
    def checkCollision(self,pos,size = 0):
        """ Returns true on collision """
        return ((self.pos[0]+ size <= pos[0]) 
                and (self.pos[0] + size + self.size[0] >= pos[0]) 
                and (self.pos[1] + size <= pos[1]) 
                and (self.pos[1] + size + self.size[1] >= pos[1]))
    
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
    
    def draw(self,screen,midpos = (450,800)):
        """ Draw circle at the ball's position"""
        temppos = getOffsetPos(self.pos,midpos)
        pygame.draw.circle(screen,(0,0,240),temppos, self.radius, self.width)
    
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
    
    def getMidInt(self):
        """ returns the center of the wall AS AN INTEGER!!"""
        return [int(self.pos[0]),int(self.pos[1])]

class movingBall(ball):
    """ Inherits from a regular ball with added motion """
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
   
    def update(self):
        """ Move the ball according to speed and bounce off of screen limits """
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        if(self.pos[0] < self.xlims[0] - self.radius 
           or self.pos[0] > self.xlims[1] + self.radius ): 
            self.vel[0] = -1*self.vel[0] 
        if(self.pos[1] < self.ylims[0] - self.radius 
           or self.pos[1] > self.ylims[1] + self.radius ): 
            self.vel[1] = -1*self.vel[1] 
    
    def restart(self):
        """ Go back to where you were at the start of the generation """
        self.pos[0] = self.startpos[0]
        self.pos[1] = self.startpos[1]
        
class rotatingRect(obstacle):
    """ Inherits from the rectangular wall, with added rotational movement! """
    def __init__(self,midPos,rectSize,vel = 0.01,startAngle = 0.5):
        self.midPos = midPos
        self.size = rectSize
        self.angle = startAngle
        self.vel = vel
        self.basePoint = ((-0.5*self.size[0],-0.5*self.size[1]),
                          (0.5*self.size[0],-0.5*self.size[1]),
                          (0.5*self.size[0],0.5*self.size[1]),
                          (-0.5*self.size[0],0.5*self.size[1]))
        
    def draw(self,screen,midpos = (450,800)):
        """ Draws the oddly oriented rectangle """
        templist = [getOffsetPos(pt,midpos) for pt in self.pointList]
        pygame.draw.polygon(screen,(0,0,240),templist)
    
    def update(self):
        self.angle += self.vel
        self.updatePointList()
    
    def updatePointList(self):
        """ Calculate where the vertices of the rectangle will moved based on 
        the angle swept per frame """
        self.pointList = []
        for bp in self.basePoint:
            temppoint = rotate(bp,self.angle)
            self.pointList.append((self.midPos[0] +temppoint[0]
                            ,self.midPos[1] +temppoint[1]))
        
    def checkCollision(self,pos,size = 0):
        """ Returns true on collision """
        temp = (pos[0] - self.midPos[0], pos[1] - self.midPos[1])
        temp = rotate(temp,-1*self.angle)     
        return ((-0.5*self.size[0]- size <= temp[0]) 
                and (0.5*self.size[0] + size + self.size[0] >= temp[0]) 
                and (-0.5*self.size[1] - size <= temp[1]) 
                and (0.5*self.size[1] + size + self.size[1] >= temp[1]))
