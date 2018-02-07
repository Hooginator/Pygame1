# -*- coding: utf-8 -*-
"""
Created on Tue Feb  6 20:44:24 2018

@author: hoog
"""

import numpy as np
import pygame

INPUTS = 22+1
INTERMEDIATE1 = 8
INTERMEDIATE2 = 6
OUTPUTS = 4

colours = [(100,120,220),(240,120,120)]
MAX_SPEED = 20

class ship:
    def __init__(self, x, y, angle,colour):
        self.startx = x
        self.starty = y
        self.startangle = angle
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.drag = 0.96
        self.angle = angle
        self.crashed = False
        self.score = 0
        self.inputColour = [colours[0] for i in range(INPUTS)]
        self.scan = np.array([0 for i in range(INPUTS)])
        self.initWeights()
        self.timeDriving = 0
        self.colour = colour
        self.checkpoint = 0
        self.laps = 0
        self.cost = [0 for i in range(6)]
    def updateSpeed(self,accel,dangle,brake):
        self.angle += dangle
        self.vx += accel * np.cos(self.angle)
        self.vy += accel * np.sin(self.angle)
        if(self.vx > MAX_SPEED): self.vx = MAX_SPEED
        if(self.vy > MAX_SPEED): self.vy = MAX_SPEED
        if(self.vx < -1*MAX_SPEED): self.vx = -1*MAX_SPEED
        if(self.vy < -1*MAX_SPEED): self.vy = -1*MAX_SPEED
        self.vx = self.vx * self.drag*(1-brake/10)
        self.vy = self.vy * self.drag*(1-brake/10)
    def updatePos(self):
        self.timeDriving +=1
        self.x += self.vx
        self.y += self.vy
    def getInputs(self,walls,width,height):
        self.inputPos = []
        distances = [40,80,120,160]
        angles = [-1.2,0.6,0,-0.6,1.2]
        
        for dis in distances:
            for ang in angles:
                self.inputPos.append([int(self.x + dis*np.cos(self.angle+ang)), int(self.y  + dis*np.sin(self.angle+ang))])
        self.inputPos.append([int(self.x + 50*np.cos(self.angle-3.1415)), int(self.y  + 50*np.sin(self.angle-3.1415))])
        i = 0
        for pos in self.inputPos:
            if(self.checkCollisions(walls,width,height)): 
                self.inputColour[i] = colours[1] 
                self.scan[i] = 1
            else: 
                self.inputColour[i] = colours[0]
                self.scan[i] = 0
            i += 1
        self.scan[i] =  int(self.getDist([self.vx,self.vy],[0,0])) # adding velocity at the end of the inputs.
    def checkCollisions(self,walls,width,height):
        for wall in walls:
            if(wall.checkCollision(self.x,self.y)): return True
            if((self.x < 0) or (self.x > width) or (self.y < 0) or (self.y > height)): return True
        return False
    def reset(self):
        self.x = self.startx
        self.y = self.starty
        self.angle = self.startangle
        self.vx = 0
        self.vy = 0
        self.crashed = False
        self.timeDriving = 0
        self.score = 0
        self.checkpoint = 0
        self.laps = 0
        self.inputColour = [colours[0] for i in range(INPUTS)]
        self.scan = np.array([0 for i in range(INPUTS)])
        self.drag = 0.96
        self.cost = [0 for i in range(6)]
                       
    def drawShip(self, screen,walls,width,height):
        pygame.draw.polygon(screen, self.colour, [[int(self.x+ 10 *np.cos(self.angle)), int(self.y+ 10 *np.sin(self.angle))],
                                   [int(self.x+ 10 *np.cos(self.angle + 2.64)), int(self.y+ 10 *np.sin(self.angle + 2.64))],
                                   [int(self.x+ 10 *np.cos(self.angle + 3.64)), int(self.y+ 10 *np.sin(self.angle + 3.64))]])
        self.getInputs(walls,width,height)
        i = 0
        for pos in self.inputPos:
            pygame.draw.circle(screen, self.inputColour[i], pos, 4,1)
            i += 1
        pygame.draw.circle(screen, (140,160,240), [int(self.x), int(self.y)], 5,2)
    def crash(self,checkpoints):
        self.cost[0] = np.abs(self.weights1).sum()
        self.cost[1] = np.abs(self.weights2).sum()
        self.cost[2] = np.abs(self.weights3).sum()
        self.cost[3] = np.abs(self.bias1).sum()
        self.cost[4] = np.abs(self.bias2).sum()
        self.cost[5] = np.abs(self.bias3).sum()
        self.totalcost = 0
        for c in self.cost:
            self.totalcost += c
        #print(str(self.totalcost))
            self.score -= 0.01*self.totalcost
        self.score += 1000
        self.score -= 0.01*self.timeDriving 
        self.score -= 0.1*self.getDist(checkpoints[self.checkpoint].getMid(),[self.x,self.y])
        self.score += self.checkpoint *1000
        self.score += self.laps * 1000 * len(checkpoints)
        self.crashed = True
        self.vx = 0
        self.vy = 0
    def getDist(self,pos1,pos2):
        return np.sqrt((pos1[0]-pos2[0])*(pos1[0]-pos2[0])+(pos1[1]-pos2[1])*(pos1[1]-pos2[1]))
    def checkCheckpoint(self,checkpoints):
        if checkpoints[self.checkpoint].checkCollision(self.x,self.y):
            self.checkpoint +=1
            if(self.checkpoint >= len(checkpoints)):
                self.checkpoint = 0
                self.laps +=1
    def initWeights(self):
        self.weights1 = np.random.normal(0,1,(INPUTS,INTERMEDIATE1))
        self.weights2 = np.random.normal(0,1,(INTERMEDIATE1,INTERMEDIATE2))
        self.weights3 = np.random.normal(0,1,(INTERMEDIATE2,OUTPUTS))
        self.bias1 = np.random.normal(0,1,(1,INTERMEDIATE1))
        self.bias2 = np.random.normal(0,1,(1,INTERMEDIATE2))
        self.bias3 = np.random.normal(0,1,(1,OUTPUTS))
    def getDecision(self):
        return np.add(np.add(np.add(self.scan.dot(self.weights1), self.bias1).dot(self.weights2),self.bias2).dot(self.weights3),self.bias3).T
    def copyAll(self,shp):
        self.copyWeights(shp, 0, shp.colour)
        self.score = shp.score
        self.x = shp.x
        self.y = shp.y
        self.checkpoint = shp.checkpoint
        self.laps = shp.laps
    def copyWeights(self, shp, stray, colour):
        if(stray == 0):
            self.weights1 = shp.weights1
            self.weights2 = shp.weights2
            self.weights3 = shp.weights3
            self.bias1 = shp.bias1
            self.bias2 = shp.bias2
            self.bias3 = shp.bias3
        else:
            self.weights1 = shp.weights1 + np.random.normal(0,stray,(INPUTS,INTERMEDIATE1))
            self.weights2 = shp.weights2 + np.random.normal(0,stray,(INTERMEDIATE1,INTERMEDIATE2))
            self.weights3 = shp.weights3 + np.random.normal(0,stray,(INTERMEDIATE2,OUTPUTS))
            self.bias1 = shp.bias1 + np.random.normal(0,stray,(1,INTERMEDIATE1))
            self.bias2 = shp.bias2 + np.random.normal(0,stray,(1,INTERMEDIATE2))
            self.bias3 = shp.bias3 + np.random.normal(0,stray,(1,OUTPUTS))
        self.colour = colour
    def copyWeightsExper(self, shp, stray, colour):
        self.copyWeights(shp, stray, colour)
        i = np.random.randint(self.weights1.shape[0])
        j = np.random.randint(self.weights1.shape[1])
        self.weights1[i,j] = np.random.normal(0,1,1)
        i = np.random.randint(self.weights2.shape[0])
        j = np.random.randint(self.weights2.shape[1])
        self.weights2[i,j] = np.random.normal(0,1,1)
        i = np.random.randint(self.weights3.shape[0])
        j = np.random.randint(self.weights3.shape[1])
        self.weights3[i,j] = np.random.normal(0,1,1)
        
        i = np.random.randint(self.bias1.shape[0])
        self.bias1[i,j] = np.random.normal(0,1,1)
        i = np.random.randint(self.bias2.shape[0])
        self.bias2[i,j] = np.random.normal(0,1,1)
        i = np.random.randint(self.bias3.shape[0])
        self.bias3[i,j] = np.random.normal(0,1,1)
        