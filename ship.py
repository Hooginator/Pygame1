# -*- coding: utf-8 -*-
"""
Created on Wed Mar 21 10:37:25 2018

@author: hoog
"""

from functions import *

# Ship constants
colours = [(100,120,220),(240,120,120)]
MAX_SPEED = 20
maxangle = 0.2
maxaccel = 1

# Ship neural net dimensions
INPUTS = 15
INTERMEDIATES = (10,7,6,5)
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
        """ Create ship with random weights """
        self.startx, self.starty, self.startangle, self.colour = x, y, angle, colour
        self.drag = 0.96
        self.initWeights()
        self.reset()
    def reset(self):
        """ Return the ship to starting location and reinitialize """
        self.x, self.y, self.angle = self.startx, self.starty, self.startangle
        self.vx, self.vy  = 0, 0
        self.crashed = False
        self.timeDriving, self.score, self.checkpoint, self.laps = 0, 0, 0, 0
        self.inputColour = [colours[0] for i in range(INPUTS)]
        self.scan = np.array([0 for i in range(INPUTS)])
        self.cost = [0 for i in range(6)]
    def initWeights(self):
        """ Initialize weights to random ones."""
        self.weights = []
        self.bias = []
        for i, dim in enumerate(DIMENSIONS[1:]):
            self.weights.append(np.random.uniform(-1,1,(DIMENSIONS[i],dim)))
            self.bias.append(np.random.uniform(-1,1,(1,dim)))
    def copyAll(self,shp):
        """ Take all properties from shp and apply them to self.  Used in determining the best ship each generation"""
        self.copyWeights(shp, 0, shp.colour)
        self.score = shp.score
        self.x = shp.x
        self.y = shp.y
        self.checkpoint = shp.checkpoint
        self.laps = shp.laps
    def copyWeights(self, shp, stray, colour):
        """ Changes weights to be around the ones of shp.  This is used to generate offspring from the shp provided."""
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
        """ saves the np array of weights for easy loading later"""
        for i,wt in enumerate(self.weights):
            np.save(filename + "_W"+str(i)+"_G" + str(generation),wt)
        for i,bs in enumerate(self.bias):
            np.save(filename + "_B"+str(i)+"_G" + str(generation),bs)
        
    def normalizeWeights(self):
        """ Make sure the weights and biases stay inside (-1,1) """
        for wt in self.weights:
            wt[wt>1] = 1
            wt[wt<-1] = -1
        for bs in self.bias:
            bs[bs>1] = 1
            bs[bs<-1] = -1
    def copyWeightsExper(self, shp, stray, colour):
        """ version of copyWeights() that only take 1 element of each weighgt matrix to change.  Might be useful. """
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
    def moveShip(self,checkpoints):
        """ Master function that is called from the main loop and goes through all the othe functions"""
        self.checkCheckpoint(checkpoints)
        angle = 0
        accel = 0   
        controlInputs = self.getDecision()
        angle -= logis(controlInputs[0]) * maxangle
        angle += logis(controlInputs[1]) * maxangle
        accel += logis(controlInputs[2]) * maxaccel
        brake =  logis(controlInputs[3])
            
        self.updateSpeed(accel,angle,brake) 
        self.updatePos()
    def checkCheckpoint(self,checkpoints):
        """Determines if we have passed a checkpoint this timestep"""
        if checkpoints[self.checkpoint].checkCollision(self.x,self.y):
            self.checkpoint +=1
            if(self.checkpoint >= len(checkpoints)):
                self.checkpoint = 0
                self.laps +=1
    def checkFuel(self,checkpointsPerLap):
        """ Returns the score received based on checkpoint progress minus the time driving.  
         If this is below 0 the sihp is said to be out of fuel and crashes"""
        return  checkFuelCost(self.checkpoint, self.laps,checkpointsPerLap)  -  self.timeDriving
    def updateSpeed(self,accel,dangle,brake):
        """ Get new vx and vy to update position"""
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
        """ Update where the ship is each timestep based on calculated velocity."""
        self.timeDriving +=1
        self.x += self.vx
        self.y += self.vy
    def getInputs(self,walls,width,height):
        """ Determine which of the input locations are in walls / out of bounds for the input vector"""
        self.inputPos = []
        distances = [50,100,150]
        angles = [1.2,0.6,0,-0.6,-1.2]
        i = 0
        
        # array of front views
        for ang in angles:
            blocked = False
            for dis in distances:
                self.inputPos.append([int(self.x + dis*np.cos(self.angle+ang)), int(self.y  + dis*np.sin(self.angle+ang))])
                if(checkCollisions(walls,self.inputPos[i],width,height) or blocked):
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
        """ Use the input vector and all the weights to decide how to control the ship this timestep."""
        temp = []
        temp.append( np.array(self.scan) )
        for i,wt in enumerate(self.weights):
            temp.append(np.add(temp[i].dot(wt),self.bias[i]))
        return temp[len(self.weights)].tolist()[0] # np.add(np.add(np.add(self.scan.dot(self.weights[0]), self.bias[0]).dot(self.weights[1]),self.bias[1]).dot(self.weights[2]),self.bias[2]).T
    
    def getScore(self,checkpoints):
        tempscore = 1000  -  0.01*self.timeDriving 
        tempscore -=  0.1*getDist(checkpoints[self.checkpoint].getMid(),[self.x,self.y])
        tempscore += self.checkpoint *1000
        tempscore += self.laps * 1000 * len(checkpoints)
        return tempscore
        
    def crash(self,checkpoints):
        """ Once the ship's run has expired it crashes.  Here its score is tallied and it is stopped until it is reset
         The cost increases as weights tend away from 0, resulting in fewer extreme weights"""
        self.cost = 0
        for wt in self.weights:
            self.cost += np.abs(wt).sum()
        for bs in self.bias:
            self.cost += np.abs(bs).sum()
        self.score -= 0.00001*self.cost
        # Score improves with distance and time driving
        self.score += self.getScore(checkpoints)
        # Stop the ship from going further
        self.crashed = True
        self.vx = 0
        self.vy = 0
        print(self.getName() + "  has crashed")
    
    ############### VISUAL #################################
    # Stuff related to creating various visual effects on screen
    ########################################################
        
    def drawShip(self,screen,walls,width,height):
        """ Draw triangular ship, get the input values and draw a red or blue circle at their location"""
        pygame.draw.polygon(screen, self.colour, [[int(self.x+ 10 *np.cos(self.angle)), int(self.y+ 10 *np.sin(self.angle))],
                                   [int(self.x+ 10 *np.cos(self.angle + 2.64)), int(self.y+ 10 *np.sin(self.angle + 2.64))],
                                   [int(self.x+ 10 *np.cos(self.angle + 3.64)), int(self.y+ 10 *np.sin(self.angle + 3.64))]])
        self.getInputs(walls,width,height)
        i = 0
        # Draw where the inputs are for decision making.
        for pos in self.inputPos:
            pygame.draw.circle(screen, self.inputColour[i], pos, 4,1)
            i += 1
        pygame.draw.circle(screen, (140,160,240), [int(self.x), int(self.y)], 5,2)
        
    def drawMatrix(self,screen):
        """ Draw a bunch of squares that light up red of green based on different points in the decision process """
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
        temp_vector = self.scan 
        # Repeat
        for j, bs in enumerate(self.bias):
            temp_vector = np.add(temp_vector.dot(self.weights[j]), bs)
            for i in range(temp_vector.shape[1]):
                temp_colour = (int(max(min((1-temp_vector[0,i])*255,255),0)),int(max(min(temp_vector[0,i]*255,255),0)),0)
                pygame.draw.rect(screen,temp_colour ,(bp[0] + (j+1)*separationy,bp[1] + separationx*i,size,size))

    def highlight(self,screen):
        """ Draw some expanding circles around the ship """
        pygame.draw.circle(screen, [max(0,tmp - (10 - self.timeDriving%10)*10) for tmp in self.colour], [int(self.x),int(self.y)], int(10+ (self.timeDriving%10 )),2)
        pygame.draw.circle(screen, self.colour, [int(self.x),int(self.y)], int(20+ (self.timeDriving%10 )),2)
        pygame.draw.circle(screen, [max(0,tmp - (self.timeDriving%10)*10) for tmp in self.colour], [int(self.x),int(self.y)], int(30+ (self.timeDriving%10 )),2)
    def getName(self):
        """ Get 6 letter "name" based on weight and bias totals """
        l = []
        for wt in self.weights:
            l.append(chr( int( 97 + (wt.sum() * 100) % 26 ) ))
        for bs in self.bias:
            l.append(chr( int( 97 + (bs.sum() * 100) % 26 ) ))
        l[0] = chr(ord(l[0]) - 32)
        return ''.join(l)
        

    