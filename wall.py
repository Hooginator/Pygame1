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
            wallArray.append([])
        j = 0 # 'j' counts the current character we are on in line 'i'
        while j < len(line):
            wallArray[i].append(line[j])
            j+=1
        i+=1
    return wallArray    
        
def mapStrFromFile(filename):
    """ Reads the file given as a string for further processing """
    with open(filename, 'r') as myfile:
        data = myfile.read()
    #print(data)
    return data

def generateObstacles(filename):
    mapArray = mapArrayFromStr(mapStrFromFile(filename+"_Wall.txt"))
    #print(mapArray)
    obstacles = []
    checkpoints = [None]*36
    i = 0
    for mapRow in mapArray:
        for j, w in enumerate(mapRow):
            if(w == '1'):
                obstacles.append(wall(layoutToPos((j,i)),(MIN_WALL_SIZE,MIN_WALL_SIZE)))
            if(str(w).isalpha()):# Alpha character,, we have acheckpoint!
                checkpoints[int(ord(w)-65)] = (wall(layoutToPos((j-1,i-1)),
                            (3*MIN_WALL_SIZE,3*MIN_WALL_SIZE)))
                
        i+=1
    while(checkpoints[-1] == None): del(checkpoints[-1])
    return mapArray, obstacles, checkpoints
   	   

##################################################################
################## general functions #############################
##################################################################


def layoutToPos(lpos):
    """ Returns the center position associated with the grid spot x, y """
    return (lpos[0]*MIN_WALL_SIZE,lpos[1]*MIN_WALL_SIZE)
def posToLayout(pos):
    """ Returns the spot in self.layout that pos would fall in.  For collision check"""
    return (int(pos[0]/MIN_WALL_SIZE),int(pos[1]/MIN_WALL_SIZE))
    

def rotate(pos,angle):
    return(pos[0]*np.cos(angle)- pos[1]*np.sin(angle),
           pos[0]*np.sin(angle)+ pos[1]*np.cos(angle))

def drawBackground(screen):
    """ Draws a black rectangle over the whole screen as a backdrop """
    screen.fill((0,0,0))

def getFuelParams(choice=0):
    """ Parameters used to determine how long each ship has for each checkpoint 
    and how quickly that time will scale down. Default is 0
    """

    fp = {0 : [200,0.8],
          1 : [300,0.6],
          2 : [500,0.9],
          3 : [500,0.9],
          }
    return fp[choice]



def myround(x, dir=1,base=MIN_WALL_SIZE):
    """ Rounds up or down to nearest integer.  YES change to move up a bit when on boundary? """
    if dir==1:
        if np.ceil(x/base) == x/base:
            return base * (np.ceil(x/base) +1)
        return base * np.ceil(x/base)
    
    if np.floor(x/base) == x/base:
        return base * (np.floor(x/base)-1)
    return base * np.floor(x/base)



def getLineOfCells(pos, angle, length_in):
    """Returns a list of tuples with the coordinates of cells that would intersect the line built from pos with angle and length also specified
    NEW PLAN: Will also return where our LOS crosses each of these boundaries
    AND the distance to each
    """
    ## Too late, rethink
    # New plan, find line equation
    # EX: at (2,3) 30 degrees 
    # y = mx +b 
    # m= tan30?
    # b=
    temp_length = 0
    grid_pos = list(posToLayout(pos))
    #print("STARTING GRIDPOS:::: ",grid_pos, " from ",pos)
    c_pos = [pos[0],pos[1]]
    s_pos = c_pos
    dxy = [np.cos(angle),np.sin(angle)]
    dixy = [int(np.sign(dxy[0])),int(np.sign(dxy[1]))]
    to_return = [((grid_pos[0],grid_pos[1]),pos,temp_length)]
    
    #print ("Done setup, onto easy cases ",dxy)
    
    if dxy[0] == 0:
        # Easy mode engaged
        n_pos = [0,0]
        i=0
        di = int(np.sign(dxy[i]))
        while temp_length < length_in:
            n_pos[1] = myround(c_pos[1]) 
            temp_length += np.abs(n_pos[1]-c_pos[1])
            c_pos[1] = n_pos[1]
            to_return.append([(grid_pos[0],grid_pos[1]+i*di),(pos[0],c_pos[1]),temp_length])
            i +=1
        return to_return
    
    if dxy[1] == 0:
        # Easy mode 2 engaged
        i=0
        n_pos = [0,0]
        di = int(np.sign(dxy[i]))
        while temp_length < length_in:
            n_pos[0] = myround(c_pos[0])
            temp_length += np.abs(n_pos[0]-c_pos[0])
            c_pos[0] = n_pos[0]
            to_return.append([(grid_pos[0]+i*di,grid_pos[1]),(c_pos[0],pos[1]),temp_length])
            i +=1
        return to_return
    
    # Not straight up or down
        
    # idea [x,y] = [t*dx+s_pos[0],t*dy+s_pos[1]]
    
    #print("DOne with simple cases, onto loop")
    
    counter_here=0
    while temp_length < length_in:
        step_lengths = [0,0]
        t_pos = [0,0]
        # Get target position for x and y's closest  grid coming up (ie where walls may start)
        for i in (0,1):
            #print("CPOS BEFORE: ",c_pos,dixy)
            t_pos[i] = myround(c_pos[i],dir=dixy[i])
            #print("TPOS BEFORE: ",t_pos)
            # Find how far the target x and y pos are from current pos
            step_lengths[i] = (t_pos[i]-c_pos[i])/dxy[i]
        
        length_to_travel = min(step_lengths)
        
        temp_length += length_to_travel 
        
        #print("New Length: ",temp_length)
        
        if temp_length > length_in:
            return to_return
            
        counter_here +=1
        if counter_here > 50:
            print ("TOK A WHILE  MID",i,c_pos,dxy,dixy,t_pos)
            
        min_index = step_lengths.index(length_to_travel)
        
        # get next pos
        n_pos = [0,0]
        
        for i in (0,1):
            if i== min_index:
                n_pos[i] = t_pos[i]
                grid_pos[i] += int(np.sign(dxy[i]))
            else:
                n_pos[i] = c_pos[i] + dxy[i]*step_lengths[1-i]
        
        to_return.append([(grid_pos[0],grid_pos[1]),(n_pos[0],n_pos[1]),temp_length])
        # Set current position up to neares t boundary
        c_pos = [n_pos[0],n_pos[1]]
        
        
        if counter_here > 50:
            print ("TOOK A WHILE  END",i,c_pos,dxy,dixy,t_pos,n_pos,dxy[i],step_lengths[1-i])
    
    return to_return
    # Next up: Bezier curves
    



    
############################################################
########### MAZE CLASS #####################################
############################################################

class maze:
    """ Master class for all the objects on the map that get in your way or 
    help """
    def __init__(self,mapName = "Map1",height = 900,width = 1600, mazeType = "circular"):
        # Load the wall and checkpoint information
        self.layout, self.obstacles, self.checkpoints = generateObstacles(mapName)
        self.checkpointsPerLap = len(self.checkpoints)
        self.screenWidth, self.screenHeight = width, height
        self.layoutHeight, self.layoutWidth = len(self.layout[:]),len(self.layout[0][:])
        self.getFuelCosts()
        self.mazeType = mazeType
            
    def getFuelCosts(self,choice = 0):
        self.fuelParams = getFuelParams(choice = choice)
        
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
        if self.isInBoundaries(pos):
            temppos = posToLayout(pos)
            return self.isWall(temppos)
        else: return 1
    
    def isWall(self,pos):
        """ Simply returns whether pos contains a wall or not.  If out of bounds returns as though wall"""
        #print(pos)
        try:
            toreturn = self.layout[pos[1]][pos[0]]
        except IndexError:
            return 1 # Out of bounds
        
        try:
            int(toreturn)
        except:
            return 0  # CHECKPOINT
        return int(toreturn) # INT WORKED, WALL or no wall

        
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
        
        
        
        
    def getMaximumSightDistance(self,pos, angle, length_in):
        """ Makses use of getLineofCells to determine where the first walls blocking LoS is (if there is one, None otherwise) 
        and returning the position where Line of Sight was broken.  This will be fed into the Matrix decisions
        and display on screen.
        
        New plan, just add this to the getLineOfCells function since it has everything we need already broken down
        """
        #print("Pre getLineOfCells")
        my_info = getLineOfCells([pos[0],pos[1]], angle, length_in)
        
        #print("Post getLineOfCells")
        for c in my_info:
            #print(c[0],c[1])
            #b=input()
            if self.isWall(c[0]) ==1:
                # WALLL HERE DO MATH TO FIND POS
                # need the intersection point
                return (c[1],c[2])
        return None
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
        
        drawRadiatingCircle(screen,temppos, frame,frame_speed=1)
        # pygame.draw.circle(screen,[max(0,tmp - (20 - frame%20)*10) for tmp in (240,240,240)],
                                   # temppos, 1 + frame %20, 1)
        # pygame.draw.circle(screen,(240,240,240),temppos, 21 + frame %20, 1)
        # pygame.draw.circle(screen,[max(0,tmp - (frame%20)*10) for tmp in (240,240,240)],
                                   # temppos, 41 + frame %20, 1)
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
