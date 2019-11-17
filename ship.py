 # -*- coding: utf-8 -*-
"""
Created on Wed Mar 21 10:37:25 2018

@author: hoog
"""

from functions import *
import os

# Ship constants
sensor_colours = [(100,100,240),(240,100,100)] # NO WALL, WALL


class ship:
    """Class for holding an indivudual racer and all the variables it needs. """
    ############### INITIALIZATION #########################
    # Functions that are run once at the start of each generation
    ########################################################

    def __init__(self,  startpos = (75,75), angle = 0, colour = (240,100,100),
                 maxSpeed = 20, maxAccel = 1, maxAngle = 0.1,
                 width = 1600, height = 900, maze = None,
                 intermediates = (8,), inputdistance = [50,100,150], inputangle = [1.2,0.6,0,-0.6,-1.2],
                 parentname = "", parentcolour = (240,100,100), name = None,orders = [1,2,3]):
        """ Creates the ship with randomly assigned weights """
        self.startpos, self.startangle, self.colour = startpos, angle, colour
        self.maxSpeed, self.maxAccel, self.maxAngle = maxSpeed, maxAccel, maxAngle
        self.maze = maze
        self.width, self.height = width, height
        self.parentname, self.parentcolour = parentname, parentcolour
        # Create dimensions array based on input, intermediate dimensions and output (4)
        self.inputType = 1 # 0: point, 1: linear
        self.setDimension(inputdistance,inputangle,intermediates,orders)
        self.drag = 0.98
        self.initWeights()
        
        if name is not None: 
            self.name = name
        else:
            self.name = self.getName()
                
        self.reset()
        
    def setDimension(self,inputdistance,inputangle,intermediates, orders):
        """ Sets parameters needed for decision making """
        if self.inputType == 0: # Matrix of angles and distances
            self.dimensions = [len(inputdistance)*len(inputangle)]
        elif self.inputType == 1: # Only angles, each one getting one input
            self.dimensions = [len(inputangle)*len(orders)]
            inputdistance = 1
            
        self.dimensions.extend(intermediates)
        self.dimensions.append(4)
        self.inputdistance, self.inputangle, self.intermediates, self.orders  = inputdistance, inputangle, intermediates, orders
      
    def reset(self):
        """ Returns the ship to its starting location and reinitializes """
        self.resetPos()
        self.vx, self.vy  = 0, 0
        self.accel, self.dangle = 0, 0
        self.crashed = False
        self.timeDriving, self.score, self.checkpoint, self.laps = 0, 0, 0, 0
        self.targetCheckpointPos = self.maze.checkpoints[0].getMidInt()
        self.inputColour = [sensor_colours[0] for i in range(self.dimensions[0])]
        self.scan = np.array([0 for i in range(self.dimensions[0])])
        self.cost = [0 for i in range(6)]
        #Extrapos for CTS LOS
        self.extrapos = []
        
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
        This is used to generate offspring from the shp provided.
        """
        self.weights = []
        self.bias = []
        if(stray == 0): # straight copy
            for i, wt in enumerate(shp.weights):
                self.weights.append(wt.copy())
            for i,bs in enumerate(shp.bias):
                self.bias.append(bs.copy())
        else: # Copy with some random added in
            for i, wt in enumerate(shp.weights):
                self.weights.append(np.add(wt.copy(), np.random.normal(0,stray,(shp.dimensions[i],shp.dimensions[i+1]))))
            for i,bs in enumerate(shp.bias):
                self.bias.append(np.add(bs.copy(), np.random.normal(0,stray,shp.dimensions[i+1])))
            self.normalizeWeights()
        self.colour = colour
        self.parentname = shp.name
        self.parentcolour = shp.colour
        self.setDimension(shp.inputdistance,shp.inputangle,shp.intermediates,shp.orders)
        
    def saveWeights(self, basename, generation):
        """ Saves the np array of weights for easy loading later"""
        for i,wt in enumerate(self.weights):
            np.save("./data/"+basename+"/"+basename + "_W"+str(i)+"_G" + str(generation),wt)
        for i,bs in enumerate(self.bias):
            np.save("./data/"+basename+"/"+basename + "_B"+str(i)+"_G" + str(generation),bs)
            
    def loadWeights(self,basename,generation,colour = None):
        temp = "./data/"+basename+"/"+basename
        self.weights = []
        done = False
        i = 0
        while(not done):
            wn = temp + "_W"+str(i)+"_G" + str(generation)+".npy"
            if(os.path.isfile(wn)):
                 self.weights.append(np.load(wn))
            else: done = True
            i += 1
            
        self.bias = []
        done = False
        i = 0
        while(not done):
            bn = temp + "_B"+str(i)+"_G" + str(generation)+".npy"
            if(os.path.isfile(bn)):
                 self.bias.append(np.load(bn))
            else: done = True
            i += 1
        if(colour is not None):
            self.colour = colour
        
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
        and changes it absolutely to a new value, regardless of the input value. 
        """
        self.copyWeights(shp, stray = stray, colour = colour)
        for wt in self.weights:
            i = np.random.randint(wt.shape[0])
            j = np.random.randint(wt.shape[1])
            wt[i,j] = np.random.uniform(-1,1,1)
        for bs in self.bias:
            i = np.random.randint(bs.shape[0])
            bs[i] = np.random.uniform(-1,1,1)
        
    ############### UPDATE #################################
    # Functions that may be used at each timestep of the race
    ########################################################    
    def moveShip(self,screen,maze):
        """ Based on the ship's brain and inputs, get a decision for this
        timestep and apply it to the acceleration, braking and turning
        """
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
        self.getInputs(maze)
    
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
            self.targetCheckpointPos = self.maze.checkpoints[self.checkpoint].getMidInt()
                    
    def checkFuel(self):
        """ Returns the score received based on checkpoint progress minus the time driving.  
         If this is below 0 the sihp is said to be out of fuel and crashes
         """
        return  self.maze.checkFuelCost(self.checkpoint,currentLap = self.laps)  -  self.timeDriving
    
    def updateSpeed(self,accel,dangle,brake):
        """ Get new vx and vy to update position"""
        self.dangle += dangle
        self.angle += self.dangle
        self.accel = accel
        self.vx += accel * np.cos(self.angle)
        self.vy += accel * np.sin(self.angle)
        # flat cap on speed
        if(self.vx > self.maxSpeed): self.vx = self.maxSpeed
        if(self.vy > self.maxSpeed): self.vy = self.maxSpeed
        if(self.vx < -1*self.maxSpeed): self.vx = -1*self.maxSpeed
        if(self.vy < -1*self.maxSpeed): self.vy = -1*self.maxSpeed
        # apply drag and braking to slow down
        self.vx = self.vx * self.drag*(1-brake/3)
        self.vy = self.vy * self.drag*(1-brake/3)
        self.dangle = self.dangle * self.drag*(1-brake/3)*0.6
        
    def updatePos(self):
        """ Update where the ship is each timestep based on calculated velocity."""
        self.timeDriving +=1
        self.pos[0] += self.vx
        self.pos[1] += self.vy
        
    def getInputs(self,maze):
        """ Determine which of the input locations are in walls / out of bounds
        for the input vector
        """
        self.inputPos = []
       
        #Extrapos for CTS LOS
        self.extrapos = []
        i,j=0,0
        # array of front views
        for ang in self.inputangle:
            blocked = False
            if self.inputType == 0:
                for dis in self.inputdistance:
                    self.inputPos.append([int(self.pos[0] + dis*np.cos(self.angle+ang)), 
                                          int(self.pos[1]  + dis*np.sin(self.angle+ang))])
                    if(maze.checkCollisions(self.inputPos[i]) or blocked):
                        blocked = True
                        self.inputColour[i] = sensor_colours[1] 
                        self.scan[i] = 0
                    else: 
                        self.inputColour[i] = sensor_colours[0]
                        self.scan[i] = 1
                    i +=1
            elif self.inputType == 1:
                #eXPERIMENTAL STUFF FOR continuous LOS
                sightlength = 200
                self.extrapos.append(maze.getMaximumSightDistance(self.pos, self.angle+ang, sightlength))
                
                if self.extrapos[i] is None:
                    temp_length = sightlength
                else:
                    temp_length = self.extrapos[i][1]
                
                for ord in self.orders:
                    self.scan[j] = temp_length**ord
                    j +=1
                i+=1
                  
    def getDecision(self):
        """ Use the input vector and all the weights to decide how to control 
        the ship this timestep.
        """
        temp = []
        temp.append( np.array(self.scan) )
        for i,wt in enumerate(self.weights):
            #print(self.bias[i],temp[i].dot(wt))
            temp.append(np.add(temp[i].dot(wt),self.bias[i]))
            #print(str(self.bias) + "   " + str(wt))
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
        weights tend away from 0, resulting in fewer extreme weights
        """
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
        self.accel = 0
        self.dangle = 0
        #print(self.getName() + "  has crashed at: " + str(self.pos[0])+ "  " + str(self.pos[1]))
    def getIntPos(self):
        """Returns the current ship position as a tuple of integers """
        return (int(self.pos[0]),int(self.pos[1]))
    
    ############### VISUAL #################################
    # Functions related to creating various visual effects on screen
    ########################################################
            
    def drawShip(self,screen,maze,midpos = (450,800),zoom = 1,fancyShip = False, drawThrusters = True):
        """ Draw triangular ship, get the input values and draw a red or blue 
        circle at their location
        """
        bp = self.getIntPos()
        bp = getOffsetPos(bp,midpos)
        
        # Draw Inputs
        if not self.crashed:
            if self.inputType == 0:
                self.drawPointInputs(screen,maze,midpos=midpos)
            elif self.inputType == 1:
                self.printExperimentalLOS(screen,midpos=midpos)
        
#        if(fancyShip): pygame.draw.polygon(screen, self.parentcolour, 
#                                [[int(bp[0]+ 10 *np.cos(self.angle+3.14)), 
#                              int(bp[1]+ 10 *np.sin(self.angle+3.14))], 
#                            [int(bp[0]+ 10 *np.cos(self.angle+1)), 
#                              int(bp[1]+ 10 *np.sin(self.angle+1))], 
#                            [int(bp[0]), 
#                              int(bp[1])], 
#                            [int(bp[0]+ 10 *np.cos(self.angle-1)), 
#                              int(bp[1]+ 10 *np.sin(self.angle-1))]])
        # draw thrusters
        
        if not self.crashed:
            if(drawThrusters):
                pygame.draw.polygon(screen, (140,140,40),
                                [[int(bp[0]+ self.accel*22 *np.cos(self.angle+3.14)), 
                                  int(bp[1]+ self.accel*22 *np.sin(self.angle+3.14))],
                                [int(bp[0]+ 7 *np.cos(self.angle + 2.64)), 
                                 int(bp[1]+ 7 *np.sin(self.angle + 2.64))],
                                [int(bp[0]+ 7 *np.cos(self.angle + 3.64)), 
                                 int(bp[1]+ 7 *np.sin(self.angle + 3.64))]])
        
        
                pygame.draw.polygon(screen, (140,140,40),
                                [[int(bp[0]+ self.dangle*60 *np.cos(self.angle-1.57) + 7*np.cos(self.angle)), 
                                  int(bp[1]+ self.dangle*60 *np.sin(self.angle-1.57) + 7*np.sin(self.angle))],
                                [int(bp[0]+ 5 *np.cos(self.angle)), 
                                 int(bp[1]+ 5 *np.sin(self.angle))],
                                [int(bp[0]+ 9 *np.cos(self.angle)), 
                                 int(bp[1]+ 9 *np.sin(self.angle))]])
    
        # draw ship
        pygame.draw.polygon(screen, self.colour, 
                            [[int(bp[0]+ 10 *np.cos(self.angle-0.15)), 
                              int(bp[1]+ 10 *np.sin(self.angle-0.15))],
                            [int(bp[0]+ 10 *np.cos(self.angle+0.15)), 
                              int(bp[1]+ 10 *np.sin(self.angle+0.15))],
                            [int(bp[0]+ 10 *np.cos(self.angle + 2.64)), 
                             int(bp[1]+ 10 *np.sin(self.angle + 2.64))],
                            [int(bp[0]+ 10 *np.cos(self.angle + 3.64)), 
                             int(bp[1]+ 10 *np.sin(self.angle + 3.64))]])
        # Draw the cockpit
        pygame.draw.circle(screen, (140,160,240), bp, 5,2)
        
    
    def drawMatrix(self,screen,pos):
        """ Draw a bunch of squares that light up red of green based on 
        different points in the decision process 
        """
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

    def drawPointInputs(self,screen,maze,midpos = (450,800)):
        bp = self.getIntPos()
        bp = getOffsetPos(bp,midpos)
        # Draw where the inputs are for decision making.
        if(self.crashed == False or True):
            self.drawTargetCheckpoint(screen,maze,bp,midpos = midpos)
            for i,pos in enumerate(self.inputPos):
                pygame.draw.circle(screen, self.inputColour[i], getOffsetPos(pos,midpos), 2,0)

    def highlight(self,screen,midpos = (800,450)):
        """ Draw some expanding circles around the ship """
        posInt = self.getIntPos()
        posInt = getOffsetPos(posInt,midpos)
        pygame.draw.circle(screen, [max(0,tmp - (10 - self.timeDriving%10)*10) for tmp in self.colour], 
                                    posInt, int(10+ (self.timeDriving%10 )),2)
        pygame.draw.circle(screen, self.colour, posInt, int(20+ (self.timeDriving%10 )),2)
        pygame.draw.circle(screen, [max(0,tmp - (self.timeDriving%10)*10) for tmp in self.colour], 
                                    posInt, int(30+ (self.timeDriving%10 )),2)
    
    def drawTargetCheckpoint(self,screen,maze,pos,midpos = (450,800)):
        """ Draw an arrow pointing to the next checkpoint we must reach """
        tarpos = getOffsetPos(self.targetCheckpointPos,midpos)
        temp = (int(pos[0]+(tarpos[0]-pos[0])/10),
                int(pos[1]+(tarpos[1]-pos[1])/10))
        pygame.draw.circle(screen,(130,240,130),temp,2,2)
    
    
    def printExperimentalLOS(self,screen,midpos = (450,800)):
        bp = self.getIntPos()
        bp = getOffsetPos(bp,midpos)
        for g in self.extrapos:
            #print("extrapos:   ",g)
            if g is not None:
                pygame.draw.circle(screen,(230,40,30),getOffsetPos(g[0],midpos),8,1)
                pygame.draw.circle(screen,(250,0,0),getOffsetPos(g[0],midpos),4,1)
                pygame.draw.line(screen,(150,150,150),bp,getOffsetPos(g[0],midpos),1)
                #pygame.draw.circle(screen,(30,140,130),[int(bp[0]),int(bp[1])],5,5)
            
   
    
    
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
            

    