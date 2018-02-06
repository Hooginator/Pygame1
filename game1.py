# -*- coding: utf-8 -*-
"""
Created on Wed Jan 24 15:08:54 2018

@author: hoog
BUG: lategame I have noticed that the top player oscillates between 2 options 
"""

import sys, pygame
import numpy as np
import copy
import os
pygame.init()

myfont = pygame.font.SysFont('Comic Sans MS', 30)

size = width, height = 1600, 900

colours = [(100,120,220),(240,120,120)]
MAX_SPEED = 20

INPUTS = 16+1
INTERMEDIATE1 = 8
INTERMEDIATE2 = 6
OUTPUTS = 4


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
    def getInputs(self):
        self.inputPos = []
        distances = [40,80,120]
        angles = [-1.2,0.6,0,-0.6,1.2]
        
        for dis in distances:
            for ang in angles:
                self.inputPos.append([int(self.x + dis*np.cos(self.angle+ang)), int(self.y  + dis*np.sin(self.angle+ang))])
        self.inputPos.append([int(self.x + 50*np.cos(self.angle-3.1415)), int(self.y  + 50*np.sin(self.angle-3.1415))])
        i = 0
        for pos in self.inputPos:
            if(checkCollisions(walls,pos[0],pos[1])): 
                self.inputColour[i] = colours[1] 
                self.scan[i] = 1
            else: 
                self.inputColour[i] = colours[0]
                self.scan[i] = 0
            i += 1
        self.scan[i] =  0 #int(getDist([self.vx,self.vy],[0,0])) # adding velocity at the end of the inputs.
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
                       
    def drawShip(self):
        pygame.draw.polygon(screen, self.colour, [[int(self.x+ 10 *np.cos(self.angle)), int(self.y+ 10 *np.sin(self.angle))],
                                   [int(self.x+ 10 *np.cos(self.angle + 2.64)), int(self.y+ 10 *np.sin(self.angle + 2.64))],
                                   [int(self.x+ 10 *np.cos(self.angle + 3.64)), int(self.y+ 10 *np.sin(self.angle + 3.64))]])
        self.getInputs()
        i = 0
        for pos in self.inputPos:
            pygame.draw.circle(screen, self.inputColour[i], pos, 4,1)
            i += 1
        pygame.draw.circle(screen, (140,160,240), [int(self.x), int(self.y)], 5,2)
    def crash(self):
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
        self.score -= 0.1*getDist(checkpoints[self.checkpoint].getMid(),[self.x,self.y])
        self.score += self.checkpoint *1000
        self.score += self.laps * 1000 * len(checkpoints)
        self.crashed = True
        self.vx = 0
        self.vy = 0
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
        
class wall:
    def __init__(self,posx,posy,sizex,sizey):
        self.posx = posx
        self.posy = posy
        self.sizex = sizex
        self.sizey = sizey
    def drawWall(self):
        pygame.draw.rect(screen,(0,0,255),(self.posx, self.posy, self.sizex, self.sizey))
    def drawCheckpoint(self):
        pygame.draw.circle(screen,(255,255,255),self.getMidInt(), 20, 3)
    def checkCollision(self,x,y):
        return ((self.posx <= x) and (self.posx + self.sizex >= x) and (self.posy <= y) and (self.posy + self.sizey >= y))
    def getMid(self):
        return [self.posx + self.sizex/2,self.posy + self.sizey/2]
    def getMidInt(self):
        return [int(self.posx + self.sizex/2),int(self.posy + self.sizey/2)]
    def maze(i):
        if(i == 0):
            return [wall(80,100,70,350),wall(150,100,300,50),wall(150,400,200,50),wall(300,250,300,50)]
        elif(i == 1):
            return [wall(200,650,1000,50),wall(200,200,50,450),wall(400,0,50,400),wall(450,350,300,50),
                    wall(850,100,50,550),wall(600,100,250,50),wall(1000,0,50,500),wall(1200,200,50,500),
                    wall(1250,200,200,50),wall(1400,400,200,50),wall(1250,650,200,50)]
    
    def checkpoints(i):
        if(i == 0):
            return [wall(0,450,150,150),wall(50,0,150,150),wall(450,50,150,150),wall(150,200,150,150),wall(250,450,150,150)]
        elif(i == 1):
            return [wall(200,0,200,200),wall(400,400,250,250),wall(750,300,100,100),wall(500,0,200,100),wall(1050,400,150,150),
            wall(1200,0,200,200),wall(1200,400,200,200),wall(1050,700,200,200),wall(0,500,200,200)]

def checkCollisions(walls,x,y):
    for wall in walls:
        if(wall.checkCollision(x,y)): return True
    if((x < 0) or (x > width) or (y < 0) or (y > height)): return True
    return False
def drawWalls(walls):
    for wall in walls: wall.drawWall()
def drawCheckpoints(walls):
    for wall in walls: wall.drawCheckpoint()
def getDist(pos1,pos2):
    return np.sqrt((pos1[0]-pos2[0])*(pos1[0]-pos2[0])+(pos1[1]-pos2[1])*(pos1[1]-pos2[1]))
def logis(a): # "Logistic function"
    b = 1/(1+np.exp(a))
    return b
maxangle = 0.1
maxaccel = 1
black = 0, 0, 0
time = pygame.time.Clock()
generation = 0

filename = "./data/BestShips"
fileext = ".txt"

ships = [ship(50,50,0,(240,100,100)) for i in range(100)]
walls = wall.maze(1)
checkpoints = wall.checkpoints(1)
screen = pygame.display.set_mode(size)
newbestsurface = [None]*3
bestship = [ship(50,50,0,(0,0,0)),ship(50,50,0,(0,0,0)),ship(50,50,0,(0,0,0))]
newBest = False
#manual = False
allcrashed = False
while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()
    
#    if(manual):
#        key = pygame.key.get_pressed()
#        if key[pygame.K_a] or key[pygame.K_LEFT]:
#            angle -= maxangle
#        if key[pygame.K_d] or key[pygame.K_RIGHT]:
#            angle += maxangle
#        if key[pygame.K_w] or key[pygame.K_UP]:
#            accel = maxaccel
#        if key[pygame.K_s] or key[pygame.K_DOWN]:
#            accel = -0.5*maxaccel
#        if key[pygame.K_SPACE]:
#            ships[0].reset()

    screen.fill(black)
    drawWalls(walls)
    #drawWalls(checkpoints)
    
        
    if(allcrashed):
        bestship = [ship(50,50,0,(0,0,0)),ship(50,50,0,(0,0,0)),ship(50,50,0,(0,0,0))]
        newBestCount = 0
        for shp in ships:
            if(shp.score > bestship[0].score):
                bestship[2].copyAll(bestship[1])
                bestship[1].copyAll(bestship[0])
                bestship[0].copyAll(shp)
                newBest = True
            elif(shp.score > bestship[1].score):
                bestship[2].copyAll(bestship[1])
                bestship[1].copyAll(shp)
            elif(shp.score > bestship[2].score):
                bestship[2].copyAll(shp)
                
        for i in range(3):
            np.save(filename + "_W1_G" + str(generation),bestship[0].weights1)
            np.save(filename +"_W2_G" +  str(generation),bestship[0].weights2)
            np.save(filename +"_W3_G" +  str(generation),bestship[0].weights3)
            np.save(filename + "_B1_G" + str(generation),bestship[0].bias1)
            np.save(filename +"_B2_G" +  str(generation),bestship[0].bias2)
            np.save(filename +"_B3_G" +  str(generation),bestship[0].bias3)
            newbestsurface[i] = myfont.render("High Score: "+str(int(bestship[i].score)) + "  (" + str(bestship[i].x) + ","+ str(bestship[i].y) +")",  False, bestship[i].colour)
           
            
        n = 0
        print("All crashed for generation " + str(generation) +"  Top Ship score: " + str(bestship[0].score) + "  at  " + str(bestship[0].weights1[0][0]))
        generation +=1
        gencoef = 1/(generation +1) 
        for shp in ships:
            if (n < 3):
                shp.copyWeights(bestship[n],0, (240-20*n,240-20*n,240-20*n))
            elif(n < 20): 
                shp.copyWeights(bestship[n%3],0.5*gencoef*gencoef, (240,100,100))
            elif(n < 40): 
                shp.copyWeights(bestship[n%3],0.5*gencoef, (240,240,100))
            elif(n < 60): 
                shp.copyWeights(bestship[n%3],1*gencoef, (100,240,100))
            elif(n < 80): 
                shp.copyWeights(bestship[n%3],5*gencoef, (100,240,240))
            elif(n < 90): 
                shp.initWeights()
                shp.colour = (100,100,240)
            elif(n < 1000): 
                shp.copyWeightsExper(bestship[n%3],5*gencoef, (240,100,240))
            n+=1
            shp.reset()
    # Move
    allcrashed = True
    for shp in ships:
        if(shp.crashed == False):
            allcrashed = False
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
            if(checkCollisions(walls,shp.x,shp.y) 
                or shp.timeDriving > 120* (1+shp.checkpoint + (len(checkpoints))*shp.laps) 
                or shp.timeDriving > 3000): shp.crash()
        shp.drawShip()
    if(newBest):
        for i in range(3):   
            screen.blit(newbestsurface[i],(0,50*(i+1)))
            pygame.draw.circle(screen, bestship[i].colour, [int(bestship[i].x),int(bestship[i].y)], 10,2)
            pygame.draw.circle(screen, bestship[i].colour, [int(bestship[i].x),int(bestship[i].y)], 20,2)
    
    textsurface = myfont.render("Gen: "+str(generation), False, (240, 240, 240))
    screen.blit(textsurface,(0,0))   
    # TESTING FOR OBS VIDEO 2
    #if(generation > 1):
    #    os.system("shutdown now")            
    time.tick(10)
    pygame.display.flip()
