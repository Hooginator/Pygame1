# -*- coding: utf-8 -*-
"""
Created on Wed Jan 24 15:08:54 2018

@author: hoog

"""

import sys, pygame
import numpy as np
import copy
import os
pygame.init()
pygame.display.init()

myfont = pygame.font.SysFont('Comic Sans MS', 30)

# Screen constants
size = width, height = 1600, 900

# Ship constants
colours = [(100,120,220),(240,120,120)]
MAX_SPEED = 20
maxangle = 0.2
maxaccel = 3

# Ship neural net dimensions
INPUTS = 15
INTERMEDIATES = (8,6)
OUTPUTS = 4
DIMENSIONS = [INPUTS]
DIMENSIONS.extend(INTERMEDIATES)
DIMENSIONS.append(OUTPUTS)


############################################################
############## SHIP CLASS ##################################
############################################################

class ship:
    ############### INITIALIZATION #########################
    # Stuff that is run once at the start of each generation
    ########################################################

    def __init__(self, x, y, angle,colour):
        # Create ship with random weights
        self.startx, self.starty, self.startangle, self.colour = x, y, angle, colour
        self.drag = 0.96
        self.initWeights()
        self.reset()
    def reset(self):
        # Return the ship to starting location and reinitialize 
        self.x, self.y, self.angle = self.startx, self.starty, self.startangle
        self.vx, self.vy  = 0, 0
        self.crashed = False
        self.timeDriving, self.score, self.checkpoint, self.laps = 0, 0, 0, 0
        self.inputColour = [colours[0] for i in range(INPUTS)]
        self.scan = np.array([0 for i in range(INPUTS)])
        self.cost = [0 for i in range(6)]
    def initWeights(self):
        # Initialize weights to random ones.
        self.weights = []
        self.bias = []
        for i, dim in enumerate(DIMENSIONS[1:]):
            self.weights.append(np.random.uniform(-1,1,(DIMENSIONS[i],dim)))
            self.bias.append(np.random.uniform(-1,1,(1,dim)))
    def copyAll(self,shp):
        # Take all properties from shp and apply them to self.  Used in determining the best ship each generation
        self.copyWeights(shp, 0, shp.colour)
        self.score = shp.score
        self.x = shp.x
        self.y = shp.y
        self.checkpoint = shp.checkpoint
        self.laps = shp.laps
    def copyWeights(self, shp, stray, colour):
        # Changes weights to be around the ones of shp.  This is used to generate offspring from the shp provided.
        if(stray == 0): # straight copy
            for i, wt in enumerate(self.weights):
                wt[:] = shp.weights[i]
            for i,bs in enumerate(self.bias):
                bs[:] = shp.bias[i]
        else: # Copy with some random added in
            for i,wt in enumerate(self.weights):
                wt[:] = shp.weights[i] + np.random.normal(0,stray,(DIMENSIONS[i],DIMENSIONS[i+1]))
            for i,bs in enumerate(self.bias):
                bs[:] = shp.bias[i] + np.random.normal(0,stray,(1,DIMENSIONS[i+1]))
            self.normalizeWeights()
        self.colour = colour
    def saveWeights(self, filename, generation):
        # saves the np array of weights for easy loading later
        for i,wt in enumerate(self.weights):
            np.save(filename + "_W"+str(i)+"_G" + str(generation),wt)
        for i,bs in enumerate(self.bias):
            np.save(filename + "_B"+str(i)+"_G" + str(generation),bs)
        
    def normalizeWeights(self):
        # Make sure the weights and biases stay inside (-1,1)
        for wt in self.weights:
            wt[wt>1] = 1
            wt[wt<-1] = -1
        for bs in self.bias:
            bs[bs>1] = 1
            bs[bs<-1] = -1
    def copyWeightsExper(self, shp, stray, colour):
        # version of copyWeights() that only take 1 element of each weighgt matrix to change.  Might be useful.
        self.copyWeights(shp, stray, colour)
        for wt in self.weights:
            i = np.random.randint(wt.shape[0])
            j = np.random.randint(wt.shape[1])
            wt[i,j] = np.random.uniform(-1,1,1)
        for bs in self.bias:
            i = np.random.randint(bs.shape[0])
            bs[i] = np.random.uniform(-1,1,1)
        
    ############### UPDATE #################################
    # Stuff that may be used at each timestep of the race
    ########################################################    
        
    def checkCheckpoint(self,checkpoints):
        # Determines if we have passed a checkpoint this timestep
        if checkpoints[self.checkpoint].checkCollision(self.x,self.y):
            self.checkpoint +=1
            if(self.checkpoint >= len(checkpoints)):
                self.checkpoint = 0
                self.laps +=1
    def checkFuel(self):
        # Returns the score received based on checkpoint progress minus the time driving.  
        # If this is below 0 the sihp is said to be out of fuel and crashes
        return  checkFuelCost(self.checkpoint, self.laps)  -  self.timeDriving
    def updateSpeed(self,accel,dangle,brake):
        # Get new vx and vy to update position
        self.angle += dangle
        self.vx += accel * np.cos(self.angle)
        self.vy += accel * np.sin(self.angle)
        # flat cap on speed
        if(self.vx > MAX_SPEED): self.vx = MAX_SPEED
        if(self.vy > MAX_SPEED): self.vy = MAX_SPEED
        if(self.vx < -1*MAX_SPEED): self.vx = -1*MAX_SPEED
        if(self.vy < -1*MAX_SPEED): self.vy = -1*MAX_SPEED
        # apply drag and braking to slow down
        self.vx = self.vx * self.drag*(1-brake/6)
        self.vy = self.vy * self.drag*(1-brake/6)
    def updatePos(self):
        # Update where the ship is each timestep based on calculated velocity.
        self.timeDriving +=1
        self.x += self.vx
        self.y += self.vy
    def getInputs(self):
        # Determine which of the input locations are in walls / out of bounds for the input vector
        self.inputPos = []
        distances = [50,100,150]
        angles = [1.2,0.6,0,-0.6,-1.2]
        i = 0
        
        # array of front views
        for ang in angles:
            blocked = False
            for dis in distances:
                self.inputPos.append([int(self.x + dis*np.cos(self.angle+ang)), int(self.y  + dis*np.sin(self.angle+ang))])
                if(checkCollisions(walls,self.inputPos[i]) or blocked):
                    blocked = True
                    self.inputColour[i] = colours[1] 
                    self.scan[i] = 0
                else: 
                    self.inputColour[i] = colours[0]
                    self.scan[i] = 1
                i += 1
        # Rear view
        #self.inputPos.append([int(self.x + 50*np.cos(self.angle-3.1415)), int(self.y  + 50*np.sin(self.angle-3.1415))]) 
                
    def getDecision(self):
        # Use the input vector and all the weights to decide how to control the ship this timestep.
        temp = []
        temp.append( np.array(self.scan) )
        for i,wt in enumerate(self.weights):
            temp.append(np.add(temp[i].dot(wt),self.bias[i]))
        return temp[len(self.weights)].tolist()[0] # np.add(np.add(np.add(self.scan.dot(self.weights[0]), self.bias[0]).dot(self.weights[1]),self.bias[1]).dot(self.weights[2]),self.bias[2]).T
    
    def crash(self):
        # Once the ship's run has expired it crashes.  Here its score is tallied and it is stopped until it is reset
        # The cost increases as weights tend away from 0, resulting in fewer extreme weights
        self.cost = 0
        for wt in self.weights:
            self.cost += np.abs(wt).sum()
        for bs in self.bias:
            self.cost += np.abs(bs).sum()
        self.score -= 0.00001*self.cost
        # Score improves with distance and time driving
        self.score += 1000
        self.score -= 0.01*self.timeDriving 
        self.score -= 0.1*getDist(checkpoints[self.checkpoint].getMid(),[self.x,self.y])
        self.score += self.checkpoint *1000
        self.score += self.laps * 1000 * len(checkpoints)
        # Stop the ship from going further
        self.crashed = True
        self.vx = 0
        self.vy = 0
        print(self.getName() + "  has crashed")
    
    ############### VISUAL #################################
    # Stuff related to creating various visual effects on screen
    ########################################################
        
    def drawShip(self):
        # Draw triangular ship, get the input values and draw a red or blue circle at their location
        pygame.draw.polygon(screen, self.colour, [[int(self.x+ 10 *np.cos(self.angle)), int(self.y+ 10 *np.sin(self.angle))],
                                   [int(self.x+ 10 *np.cos(self.angle + 2.64)), int(self.y+ 10 *np.sin(self.angle + 2.64))],
                                   [int(self.x+ 10 *np.cos(self.angle + 3.64)), int(self.y+ 10 *np.sin(self.angle + 3.64))]])
        self.getInputs()
        i = 0
        # Draw where the inputs are for decision making.
        for pos in self.inputPos:
            pygame.draw.circle(screen, self.inputColour[i], pos, 4,1)
            i += 1
        pygame.draw.circle(screen, (140,160,240), [int(self.x), int(self.y)], 5,2)
        
    def drawMatrix(self):
        # Draw a bunch of squares that light up red of green based on different points in the decision process 
        bp = [50,750] # base position bp
        namesurface = myfont.render(self.getName(), False, self.colour)
        screen.blit(namesurface,(bp[0],bp[1] -40),)  
        size = 10
        separationx = 12
        separationy = 20
        # Cycle through array of inputs
        for i in range(INPUTS):
            # Create red - green colour based on array
            temp_colour = (int((1-self.scan[i])*255),int(self.scan[i]*255),0)
            # Draw square that is slightly offset of previous square
            pygame.draw.rect(screen,temp_colour ,(bp[0] - separationx *int(i / 3),bp[1] - separationx*(i%3) + 3*separationx,size,size))
        # Calculate intermediate decision array
        temp_vector = np.add(self.scan.dot(self.weights[0]), self.bias[0])
        # Repeat
        for i in range(temp_vector.shape[1]):
            temp_colour = (int(max(min((1-temp_vector[0,i])*255,255),0)),int(max(min(temp_vector[0,i]*255,255),0)),0)
            pygame.draw.rect(screen,temp_colour ,(bp[0] + separationy,bp[1] + separationx*i,size,size))
        temp_vector = np.add(temp_vector.dot(self.weights[1]), self.bias[1])
        for i in range(temp_vector.shape[1]):
            temp_colour = (int(max(min((1-temp_vector[0,i])*255,255),0)),int(max(min(temp_vector[0,i]*255,255),0)),0)
            pygame.draw.rect(screen,temp_colour ,(bp[0] + 2*separationy,bp[1] + separationx*i,size,size))
        temp_vector = np.add(temp_vector.dot(self.weights[2]), self.bias[2])
        for i in range(temp_vector.shape[1]):
            temp_colour = (int(max(min((1-temp_vector[0,i])*255,255),0)),int(max(min(temp_vector[0,i]*255,255),0)),0)
            pygame.draw.rect(screen,temp_colour ,(bp[0] + 3*separationy,bp[1] + separationx*i,size,size))
    def highlight(self):
            pygame.draw.circle(screen, [min(255,tmp + (self.timeDriving%10-5)*0) for tmp in self.colour], [int(self.x),int(self.y)], int(10+ (self.timeDriving%10 )),2)
            pygame.draw.circle(screen, [min(255,tmp + (self.timeDriving%10-5)*0) for tmp in self.colour], [int(self.x),int(self.y)], int(20+ (self.timeDriving%10 )),2)
            pygame.draw.circle(screen, [min(255,tmp + (self.timeDriving%10-5)*0) for tmp in self.colour], [int(self.x),int(self.y)], int(30+ (self.timeDriving%10 )),2)
    def getName(self):
        # Get 6 letter "name" based on weight and bias totals
        l = [0 for i in range(6)]        
        l[0] = chr( int( 97 - 32 + (self.weights[0].sum() * 100) % 26 ) )
        l[1] = chr( int( 97 + (self.weights[1].sum() * 100) % 26 ) )
        l[2] = chr( int( 97 + (self.weights[2].sum() * 100) % 26 ) )
        l[3] = chr( int( 97 + (self.bias[0].sum() * 100) % 26 ) )
        l[4] = chr( int( 97 + (self.bias[1].sum() * 100) % 26 ) )
        l[5] = chr( int( 97 + (self.bias[2].sum() * 100) % 26 ) )
        return ''.join(l)
        

    
        
   


############################################################
########### WALL CLASS #####################################
############################################################

     
class wall:
    # for impassable walls and checkpoints
    def __init__(self,posx,posy,sizex,sizey):
        self.posx = posx
        self.posy = posy
        self.sizex = sizex
        self.sizey = sizey
    def drawWall(self):
        pygame.draw.rect(screen,(0,0,255),(self.posx, self.posy, self.sizex, self.sizey))
    def drawCheckpoint(self):
        # Less intrusive draw for checkpoints
        pygame.draw.circle(screen,(255,255,255),self.getMidInt(), 20, 3)
    def checkCollision(self,pos):
        return self.checkCollision(self,pos[0],pos[1])
    def checkCollision(self,x,y):
        # determine if position (x,y) is crashed
        return ((self.posx <= x) and (self.posx + self.sizex >= x) and (self.posy <= y) and (self.posy + self.sizey >= y))
    def getMid(self):
        # returns the center of the wall
        return [self.posx + self.sizex/2,self.posy + self.sizey/2]
    def getMidInt(self):
        # returns the center of the wall AS AN INTEGER!!
        return [int(self.posx + self.sizex/2),int(self.posy + self.sizey/2)]
    def maze(i):
        # Here is the "savefile" of my mazes or maps.  
        if(i == 0):
            return [wall(80,100,70,350),wall(150,100,300,50),wall(150,400,200,50),wall(300,250,300,50)]
        elif(i == 1):
            return [wall(200,650,1000,50),wall(200,200,50,450),wall(400,0,50,400),wall(450,350,300,50),
                    wall(850,100,50,550),wall(600,100,250,50),wall(1000,0,50,500),wall(1200,200,50,500),
                    wall(1250,200,200,50),wall(1400,400,200,50),wall(1250,650,200,50)]
    
    def checkpoints(i):
        # Here is the "savefile" of my checkpoints corresponding to the above maps.  
        if(i == 0):
            return [wall(0,450,150,150),wall(50,0,150,150),wall(450,50,150,150),wall(150,200,150,150),wall(250,450,150,150)]
        elif(i == 1):
            return [wall(200,0,200,200),wall(400,400,250,250),wall(750,300,100,100),wall(450,0,200,100),wall(900,0,100,150),wall(1050,400,150,150),
            wall(1450,100,150,150),wall(1250,400,150,150),wall(1400,650,200,200),wall(0,500,200,200)]


############################################################
########### FUNCTIONS ######################################
############################################################



def checkCollisions(walls,pos):
    # Checks pos (x,y) against all walls for collision
    for wall in walls:
        if(wall.checkCollision(pos[0],pos[1])): return True
    if((pos[0] < 0) or (pos[0] > width) or (pos[1] < 0) or (pos[1] > height)): return True
    return False
def drawWalls(walls):
    # Create blocking visual for the list of walls given
    for wall in walls: wall.drawWall()
def drawCheckpoints(walls):
    # Create small checkpointvisual for the list of walls given
    for wall in walls: wall.drawCheckpoint()
def getDist(pos1,pos2):
    # returns the pythagorean distance between 2 vectors
    return np.sqrt((pos1[0]-pos2[0])*(pos1[0]-pos2[0])+(pos1[1]-pos2[1])*(pos1[1]-pos2[1]))
def logis(a): 
    # "Logistic function"
    b = 1/(1+np.exp(a))
    return b
def checkFuelCost(CHPTS, LAPS):
        return  50 + 200*(LAPS * checkpointPerLap + CHPTS )** 0.8
    
    

############################################################
########## MAIN PROGRAM ####################################
############################################################
    
# Initialization     
time = pygame.time.Clock()
generation = 0
nseeds = 10

filename = "./data/BestShips"
fileext = ".txt"

ships = [ship(50,50,0,(240,100,100)) for i in range(100)]
walls = wall.maze(1)
checkpoints = wall.checkpoints(1)
checkpointPerLap = len(checkpoints)
screen = pygame.display.set_mode(size)
newbestsurface = [None]*nseeds
newBest = False
#manual = False
allcrashed = False
while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()
    screen.fill((0,0,0))
    drawWalls(walls)
    #drawWalls(checkpoints)
    
    # Once everyone has crashed / run out of fuel we restart at the next generation
    if(allcrashed):
        # Determine best ships
        ships.sort(key = lambda x: x.score, reverse = True)
        bestship = copy.deepcopy(ships[0:nseeds])
        newBest = True
        # Save top of each generation
        bestship[0].saveWeights(filename, generation)
        # Create surface for a high score table
        for i in range(min(nseeds,10)):
            newbestsurface[i] = myfont.render(str(i) + ":   " + str(int(bestship[i].score)) +"   "+bestship[i].getName(),  False, bestship[i].colour)
           
            
        n = 0
        print("All crashed for generation " + str(generation) +"  Top Ship score: " + str(bestship[0].score) + "  at  " + str(bestship[0].weights[0][0][0]))
        generation +=1
        gencoef = 1/(generation +1) 
        for shp in ships:
            if(n < 20): 
                shp.copyWeights(bestship[n%nseeds],0.1*gencoef*gencoef, (240,100,100))
            elif(n < 40): 
                shp.copyWeights(bestship[n%nseeds],0.1*gencoef, (240,240,100))
            elif(n < 60): 
                shp.copyWeights(bestship[n%nseeds],0.5*gencoef, (100,240,100))
            elif(n < 80): 
                shp.copyWeights(bestship[n%nseeds],1*gencoef, (100,240,240))
            elif(n < 90): 
                shp.initWeights()
                shp.colour = (100,100,240)
            elif(n < 1000): 
                shp.copyWeightsExper(bestship[n%nseeds],1*gencoef, (240,100,240))
            n+=1
            shp.reset()
    # Move
    allcrashed = True
    for shp in ships:
        if(shp.crashed == False):
            shp.checkCheckpoint(checkpoints)
            angle = 0
            accel = 0   
            controlInputs = shp.getDecision()
            angle -= logis(controlInputs[0]) * maxangle
            angle += logis(controlInputs[1]) * maxangle
            accel += logis(controlInputs[2]) * maxaccel
            brake =  logis(controlInputs[3])
            
            shp.updateSpeed(accel,angle,brake) 
            shp.updatePos()
            if(checkCollisions(walls,[shp.x,shp.y]) 
                or shp.checkFuel() < 0): shp.crash()
            if(allcrashed): 
                shp.drawMatrix()
                shp.highlight()
                allcrashed = False
        shp.drawShip()
    if(newBest):
        for i in range(min(nseeds,10)):   
            screen.blit(newbestsurface[i],(0,50*(i+4)))
            pygame.draw.circle(screen, bestship[i].colour, [int(bestship[i].x),int(bestship[i].y)], 10,2)
            pygame.draw.circle(screen, bestship[i].colour, [int(bestship[i].x),int(bestship[i].y)], 20,2)
    
    textsurface = myfont.render("Gen: "+str(generation), False, (240, 240, 240))
    screen.blit(textsurface,(0,0))   
    # TESTING FOR OBS VIDEO 2
    #if(generation > 1):
    #    os.system("shutdown now")            
    time.tick(30)
    pygame.display.flip()
