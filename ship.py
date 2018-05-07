# -*- coding: utf-8 -*-
"""
Created on Wed Mar 21 10:37:25 2018

@author: hoog
"""

from functions import *
import os
# Ship constants
colours = [(100,100,240),(240,100,100)]


############################################################
############## SHIP CLASS ##################################
############################################################

class ship:
    """Class for holding an indivudual racer and all the variables it needs. """
    ############### INITIALIZATION #########################
    # Stuff that is run once at the start of each generation
    ########################################################

    def __init__(self,  startpos = [50,50], angle = 0, colour = (240,100,100),
                 maxSpeed = 20, maxAccel = 1, maxAngle = 0.2,
                 width = 1600, height = 900, maze = None,
                 intermediates = (8,), inputdistance = [50,100,150], inputangle = [1.2,0.6,0,-0.6,-1.2],
                 parentname = "", parentcolour = (240,100,100), name = None):
        """ Creates the ship with randomly assigned weights """
        self.startpos, self.startangle, self.colour = startpos, angle, colour
        self.maxSpeed, self.maxAccel, self.maxAngle = maxSpeed, maxAccel, maxAngle
        self.maze = maze
        self.width, self.height = width, height
        self.parentname, self.parentcolour = parentname, parentcolour
        # Create dimensions array based on input, intermediate dimensions and output (4)
        self.dimensions = [len(inputdistance)*len(inputangle)]
        self.dimensions.extend(intermediates)
        self.dimensions.append(4)
        self.inputdistance, self.inputangle,  = inputdistance, inputangle
        self.drag = 0.96
        self.initWeights()
        if name is not None: 
            self.name = name
        else:
            self.name = self.getName()
                
        self.reset()
        
        
      
    def reset(self):
        """ Returns the ship to its starting location and reinitializes """
        self.resetPos()
        self.vx, self.vy  = 0, 0
        self.crashed = False
        self.timeDriving, self.score, self.checkpoint, self.laps = 0, 0, 0, 0
        self.inputColour = [colours[0] for i in range(self.dimensions[0])]
        self.scan = np.array([0 for i in range(self.dimensions[0])])
        self.cost = [0 for i in range(6)]
        
    def resetPos(self):
        """ Go back to start location """
        self.angle = self.startangle
        self.pos = []
        self.pos.extend(self.startpos)
        
    def newSpawn(self, colour = (100,100,240)):
        self.initWeights()
        self.name = self.getName()
        self.parentname = ""
        self.parentcolour = colour
        
    def initWeights(self):
        """ Initializes weights to randomly selected ones."""
        self.weights = []
        self.bias = []
        for i, dim in enumerate(self.dimensions[1:]):
            self.weights.append(np.random.uniform(-1,1,(self.dimensions[i],dim)))
            self.bias.append(np.random.uniform(-1,1,dim))
            
    def copyWeights(self, shp, stray = 0, colour = (240,100,100)):
        """ Changes weights to be around the ones provided by shp.  
        This is used to generate offspring from the shp provided."""
        if(stray == 0): # straight copy
            for i, wt in enumerate(self.weights):
                wt[:] = shp.weights[i]
            for i,bs in enumerate(self.bias):
                bs[:] = shp.bias[i]
        else: # Copy with some random added in
            for i,wt in enumerate(self.weights):
                wt[:] = shp.weights[i] + np.random.normal(0,stray,(self.dimensions[i],self.dimensions[i+1]))
            for i,bs in enumerate(self.bias):
                bs[:] = shp.bias[i] + np.random.normal(0,stray,(1,self.dimensions[i+1]))
            self.normalizeWeights()
        self.colour = colour
        self.parentname = shp.name
        self.parentcolour = shp.colour
        
    def saveWeights(self, basename, generation):
        """ Saves the np array of weights for easy loading later"""
        if not os.path.exists("./data/"+basename):
            os.makedirs("./data/"+basename)
        for i,wt in enumerate(self.weights):
            np.save("./data/"+basename+"/"+basename + "_W"+str(i)+"_G" + str(generation),wt)
        for i,bs in enumerate(self.bias):
            np.save("./data/"+basename+"/"+basename + "_B"+str(i)+"_G" + str(generation),bs)
            
    def loadWeights(self,basename,generation):
        temp = "./data/"+basename+"/"+basename
        print (temp)
        for i, wt in enumerate(self.weights):  
            wn = temp + "_W"+str(i)+"_G" + str(generation)+".npy"
            if(os.path.isfile(wn)):
                wt[:] = np.load(wn)
            else: print ("No file found for: " + wn)
        for i,bs in enumerate(self.bias):
            bn = temp + "_B"+str(i)+"_G" + str(generation)+".npy"
            if(os.path.isfile(bn)):
                bs[:] = np.load(bn)
            else: print ("No file found for: " + bn)
        
    def normalizeWeights(self):
        """ Make sure the weights and biases stay inside (-1,1) """
        for wt in self.weights:
            wt[wt>1] = 1
            wt[wt<-1] = -1
        for bs in self.bias:
            bs[bs>1] = 1
            bs[bs<-1] = -1
    def copyWeightsExper(self, shp, stray = 0, colour = (240,100,100)):
        """ version of copyWeights() that only take 1 element of each weight matrix 
        and changes it absolutely to a new value, regardless of the input value. """
        self.copyWeights(shp, stray = stray, colour = colour)
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
    def moveShip(self,screen):
        """ Based on the ship's brain and inputs, get a decision for this
        timestep and apply it to the acceleration, braking and turning"""
        self.checkCheckpoint()
        angle = 0
        accel = 0   
        controlInputs = self.getDecision()
        angle -= logis(controlInputs[0]) * self.maxAngle
        angle += logis(controlInputs[1]) * self.maxAngle
        accel += logis(controlInputs[2]) * self.maxAccel
        brake =  logis(controlInputs[3])
            
        self.updateSpeed(accel,angle,brake) 
        self.updatePos()
    def checkCheckpoint(self):
        """Determines if we have passed a checkpoint this timestep"""
        if self.maze.checkpoints[self.checkpoint].checkCollision(self.pos):
            self.checkpoint +=1
            if(self.checkpoint >= self.maze.checkpointsPerLap):
                if(self.maze.mazeType == "circular"):
                    self.checkpoint = 0
                    self.laps +=1
                elif(self.maze.mazeType == "linear"):
                    self.checkpoint = 0
                    self.laps +=1
                    self.resetPos()
                    
    def checkFuel(self):
        """ Returns the score received based on checkpoint progress minus the time driving.  
         If this is below 0 the sihp is said to be out of fuel and crashes"""
        return  self.maze.checkFuelCost(self.checkpoint,currentLap = self.laps)  -  self.timeDriving
    def updateSpeed(self,accel,dangle,brake):
        """ Get new vx and vy to update position"""
        self.angle += dangle
        self.vx += accel * np.cos(self.angle)
        self.vy += accel * np.sin(self.angle)
        # flat cap on speed
        if(self.vx > self.maxSpeed): self.vx = self.maxSpeed
        if(self.vy > self.maxSpeed): self.vy = self.maxSpeed
        if(self.vx < -1*self.maxSpeed): self.vx = -1*self.maxSpeed
        if(self.vy < -1*self.maxSpeed): self.vy = -1*self.maxSpeed
        # apply drag and braking to slow down
        self.vx = self.vx * self.drag*(1-brake/6)
        self.vy = self.vy * self.drag*(1-brake/6)
    def updatePos(self):
        """ Update where the ship is each timestep based on calculated velocity."""
        self.timeDriving +=1
        self.pos[0] += self.vx
        self.pos[1] += self.vy
    def getInputs(self,maze):
        """ Determine which of the input locations are in walls / out of bounds
        for the input vector"""
        self.inputPos = []
        i = 0
        
        # array of front views
        for ang in self.inputangle:
            blocked = False
            for dis in self.inputdistance:
                self.inputPos.append([int(self.pos[0] + dis*np.cos(self.angle+ang)), 
                                      int(self.pos[1]  + dis*np.sin(self.angle+ang))])
                if(maze.checkCollisions(self.inputPos[i]) or blocked):
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
        """ Use the input vector and all the weights to decide how to control 
        the ship this timestep."""
        temp = []
        temp.append( np.array(self.scan) )
        for i,wt in enumerate(self.weights):
            temp.append(np.add(temp[i].dot(wt),self.bias[i]))
        return temp[len(self.weights)].tolist() # np.add(np.add(np.add(self.scan.dot(self.weights[0]), self.bias[0]).dot(self.weights[1]),self.bias[1]).dot(self.weights[2]),self.bias[2]).T
    
    def getScore(self):
        """ determine the current score of the ship """
        tempscore = 1000  -  0.01*self.timeDriving 
        tempscore -=  0.1*getDist(self.maze.checkpoints[self.checkpoint].getMid(),self.pos)
        tempscore += self.checkpoint *1000
        tempscore += self.laps * 1000 * len(self.maze.checkpoints)
        return tempscore
        
    def crash(self):
        """ Once the ship's run has expired it crashes.  Here its score is 
        tallied and it is stopped until it is reset The cost increases as 
        weights tend away from 0, resulting in fewer extreme weights"""
        self.cost = 0
        for wt in self.weights:
            self.cost += np.abs(wt).sum()
        for bs in self.bias:
            self.cost += np.abs(bs).sum()
        self.score -= 0.00001*self.cost
        # Score improves with distance and time driving
        self.score += self.getScore()
        # Stop the ship from going further
        self.crashed = True
        self.vx = 0
        self.vy = 0
        #print(self.getName() + "  has crashed at: " + str(self.pos[0])+ "  " + str(self.pos[1]))
    def getIntPos(self):
        return (int(self.pos[0]),int(self.pos[1]))
    ############### VISUAL #################################
    # Stuff related to creating various visual effects on screen
    ########################################################
        
    def drawShip(self,screen,maze):
        """ Draw triangular ship, get the input values and draw a red or blue 
        circle at their location"""
        posInt = self.getIntPos()
        pygame.draw.polygon(screen, self.colour, [[int(posInt[0]+ 10 *np.cos(self.angle)), int(posInt[1]+ 10 *np.sin(self.angle))],
                                   [int(posInt[0]+ 10 *np.cos(self.angle + 2.64)), int(posInt[1]+ 10 *np.sin(self.angle + 2.64))],
                                   [int(posInt[0]+ 10 *np.cos(self.angle + 3.64)), int(posInt[1]+ 10 *np.sin(self.angle + 3.64))]])
        self.getInputs(maze)
        i = 0
        # Draw where the inputs are for decision making.
        if(self.crashed == False):
            for pos in self.inputPos:
                pygame.draw.circle(screen, self.inputColour[i], pos, 4,1)
                i += 1
        pygame.draw.circle(screen, (140,160,240), posInt, 5,2)
        
    def drawMatrix(self,screen,pos):
        """ Draw a bunch of squares that light up red of green based on 
        different points in the decision process """
        bp = pos # base position bp
        namesurface = myfont.render(self.parentname, False, self.parentcolour)
        screen.blit(namesurface,(bp[0]-50,bp[1] -60),) 
        tempOffset = namesurface.get_width()
        namesurface = myfont.render(self.name, False, self.colour)
        screen.blit(namesurface,(bp[0]-40 ,bp[1]-30),) 
        size = 10
        separationx = 12
        separationy = 20
        # Cycle through array of inputs
        for i in range(self.dimensions[0]):
            # Create red - green colour based on array
            temp_colour = (int((1-self.scan[i])*240),int(self.scan[i]*240),0)
            # Draw square that is slightly offset of previous square
            pygame.draw.rect(screen,temp_colour ,(bp[0] - separationx *int(i / len(self.inputdistance)),
                                                  bp[1] - separationx*(i%len(self.inputdistance)) + 3*separationx,size,size))
        # Calculate intermediate decision array
        temp_vector = self.scan 
        # Repeat
        for j, bs in enumerate(self.bias):
            temp_vector = np.add(temp_vector.dot(self.weights[j]), bs)
            for i in range(temp_vector.shape[0]):
                temp_colour = (int(max(min((1-temp_vector[i])*240,240),0)),int(max(min(temp_vector[i]*240,240),0)),0)
                pygame.draw.rect(screen,temp_colour ,(bp[0] + (j+1)*separationy,bp[1] + separationx*i,size,size))

    def highlight(self,screen):
        """ Draw some expanding circles around the ship """
        posInt = self.getIntPos()
        pygame.draw.circle(screen, [max(0,tmp - (10 - self.timeDriving%10)*10) for tmp in self.colour], 
                                    posInt, int(10+ (self.timeDriving%10 )),2)
        pygame.draw.circle(screen, self.colour, posInt, int(20+ (self.timeDriving%10 )),2)
        pygame.draw.circle(screen, [max(0,tmp - (self.timeDriving%10)*10) for tmp in self.colour], 
                                    posInt, int(30+ (self.timeDriving%10 )),2)
    def getName(self):
        """ Get 6 letter "name" based on weight and bias totals """
        l = []
        for wt in self.weights:
            l.append(chr( int( 97 + (sum(map(sum,wt)) * 10) % 26 ) ))
        for bs in self.bias:
            #print("BS: "+str(bs[0]))
            l.append(chr( int( 97 + (sum(bs) * 10) % 26 ) ))
        l[0] = chr(ord(l[0]) - 32)
        self.name = ''.join(l)
        return self.name
    def setName(self,newName):
        """ Changes the weights and biases randomly in order to have the 
        getName() function return the name specified here """
        for i, wt in enumerate(self.weights):
            tempcoef = 0
            tempoff = ord(newName[i]) - ord(self.getName()[i])
            if(tempoff > 0): 
                tempcoef = 0.1
            else: 
                tempcoef = -0.1
            #print("Was:  "+newName + "  " + self.getName() + "   " + str(tempoff))
            tempoff = np.abs(tempoff)
            for j in range(tempoff):    
                a = np.random.randint(wt.shape[0])
                b = np.random.randint(wt.shape[1])
                wt[a,b] += tempcoef

        for v, bs in enumerate(self.bias):
            tempcoef = 0
            tempoff = ord(newName[v+len(self.weights)]) - ord(self.getName()[v+len(self.weights)])
            if(tempoff > 0): 
                tempcoef = 0.1
            else: 
                tempcoef = -0.1
            #print("Now:  "+ str(v) + "  " +newName + "  " + self.getName() + "   " + str(tempoff))
            tempoff = np.abs(tempoff)
            for j in range(tempoff):    
                c = np.random.randint(bs.shape[0])
                bs[c] += tempcoef
    def nameShip(self,newName,colour = None):
        """ Forces the ship to conform to the name and colour provided """
        self.setName(newName)
        if colour is not None:
            self.colour = colour
            

    