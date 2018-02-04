# -*- coding: utf-8 -*-
"""
Created on Wed Jan 24 15:08:54 2018

@author: hoog
BUG: lategame I have noticed that the top player oscillates between 2 options 
"""

import sys, pygame
import numpy as np
import copy
pygame.init()

myfont = pygame.font.SysFont('Comic Sans MS', 30)

size = width, height = 1600, 900

colours = [(100,120,220),(240,120,120)]
MAX_SPEED = 20

INPUTS = 11+1
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
        self.drag = 0.95
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
    def updateSpeed(self,accel,dangle,brake):
        if np.abs(dangle > 0.1): print("sdfghjkl")
        self.angle += dangle
        self.vx += accel * np.cos(self.angle)
        self.vy += accel * np.sin(self.angle)
        if(self.vx > MAX_SPEED): self.vx = MAX_SPEED
        if(self.vy > MAX_SPEED): self.vy = MAX_SPEED
        if(self.vx < -1*MAX_SPEED): self.vx = -1*MAX_SPEED
        if(self.vy < -1*MAX_SPEED): self.vy = -1*MAX_SPEED
        self.vx = self.vx * self.drag*(1-brake/2)
        self.vy = self.vy * self.drag*(1-brake/2)
    def updatePos(self):
        self.timeDriving +=1
        self.x += self.vx
        self.y += self.vy
    def getInputs(self):
        self.inputPos = [[int(self.x + 50*np.cos(self.angle-0.5)), int(self.y  + 50*np.sin(self.angle-0.5))],
                     [int(self.x + 50*np.cos(self.angle+0.5)), int(self.y  + 50*np.sin(self.angle+0.5))],
                      [int(self.x + 50*np.cos(self.angle-1)), int(self.y  + 50*np.sin(self.angle-1))],
                       [int(self.x + 50*np.cos(self.angle+1)), int(self.y  + 50*np.sin(self.angle+1))],
                        [int(self.x + 100*np.cos(self.angle-0.5)), int(self.y  + 100*np.sin(self.angle-0.5))],
                     [int(self.x + 100*np.cos(self.angle+0.5)), int(self.y  + 100*np.sin(self.angle+0.5))],
                      [int(self.x + 100*np.cos(self.angle-1)), int(self.y  + 100*np.sin(self.angle-1))],
                       [int(self.x + 100*np.cos(self.angle+1)), int(self.y  + 100*np.sin(self.angle+1))],
                       [int(self.x + 100*np.cos(self.angle)), int(self.y  + 100*np.sin(self.angle))],
                       [int(self.x + 50*np.cos(self.angle)), int(self.y  + 50*np.sin(self.angle))],
                       [int(self.x + 50*np.cos(self.angle + 3.14)), int(self.y  + 50*np.sin(self.angle + 3.14))]]
        i = 0
        for pos in self.inputPos:
            if(checkCollisions(walls,pos[0],pos[1])): 
                self.inputColour[i] = colours[1] 
                self.scan[i] = 1
            else: 
                self.inputColour[i] = colours[0]
                self.scan[i] = 0
            i += 1
        self.scan[i] = int(getDist([self.vx,self.vy],[0,0])) # adding velocity at the end of the inputs.
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
        self.score += 1000
        #self.score -= 0.1*self.timeDriving 
        self.score -= 0.1*getDist(checkpoints[self.checkpoint].getMid(),[self.x,self.y])
        self.score += self.checkpoint *1000
        self.score += self.laps * 4000
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
    def copyWeights(self, ship, stray, colour):
        if(stray == 0):
            self.weights1 = ship.weights1
            self.weights2 = ship.weights2
            self.weights3 = ship.weights3
            self.bias1 = ship.bias1
            self.bias2 = ship.bias2
            self.bias3 = ship.bias3
        else:
            self.weights1 = ship.weights1 + np.random.normal(0,stray,(INPUTS,INTERMEDIATE1))
            self.weights2 = ship.weights2 + np.random.normal(0,stray,(INTERMEDIATE1,INTERMEDIATE2))
            self.weights3 = ship.weights3 + np.random.normal(0,stray,(INTERMEDIATE2,OUTPUTS))
            self.bias1 = ship.bias1 + np.random.normal(0,stray,(1,INTERMEDIATE1))
            self.bias2 = ship.bias2 + np.random.normal(0,stray,(1,INTERMEDIATE2))
            self.bias3 = ship.bias3 + np.random.normal(0,stray,(1,OUTPUTS))
        self.colour = colour
    def copyWeightsExper(self, ship, stray, colour):
        self.weights1 = ship.weights1 + np.random.beta(0.5,0.5,(INPUTS,INTERMEDIATE1))*stray
        self.weights2 = ship.weights2 + np.random.beta(0.5,0.5,(INTERMEDIATE1,INTERMEDIATE2))*stray
        self.weights3 = ship.weights3 + np.random.beta(0.5,0.5,(INTERMEDIATE2,OUTPUTS))*stray
        self.bias1 = ship.bias1 + np.random.beta(0.5,0.5,(1,INTERMEDIATE1))*stray
        self.bias2 = ship.bias2 + np.random.beta(0.5,0.5,(1,INTERMEDIATE2))*stray
        self.bias3 = ship.bias3 + np.random.beta(0.5,0.5,(1,OUTPUTS))*stray
        self.colour = colour
        
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
                    wall(850,100,50,550),wall(600,100,250,50),wall(1000,0,50,500),wall(1200,200,50,500),]
    
    def checkpoints(i):
        if(i == 0):
            return [wall(0,450,150,150),wall(50,0,150,150),wall(450,50,150,150),wall(150,200,150,150),wall(250,450,150,150)]
        elif(i == 1):
            return [wall(400,400,250,250),wall(750,300,100,100),wall(600,0,100,100),wall(1050,350,150,150),
            wall(1200,0,200,200),wall(1050,700,200,200),wall(0,500,200,200),wall(200,0,200,200)]

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

ships = [ship(50,50,0,(240,100,100)) for i in range(100)]
walls = wall.maze(1)
checkpoints = wall.checkpoints(1)
for shp in ships: shp.getInputs()
screen = pygame.display.set_mode(size)
newbestsurface = [None]*3
bestship = [ship(550,450,-3.1415,(240,100,100)),ship(550,450,-3.1415,(240,100,100)),ship(550,450,-3.1415,(240,100,100))]
newBest = False
#manual = False
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
    textsurface = myfont.render("Gen: "+str(generation), False, (240, 240, 240))
    screen.blit(textsurface,(0,0))
    #drawWalls(checkpoints)
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
                or shp.timeDriving > 150* (1.5+shp.checkpoint + 4*shp.laps) 
                or shp.timeDriving > 3000): shp.crash()
        shp.drawShip()
        
    if(allcrashed):
        bestship = [ship(550,450,-3.1415,(240,100,100)),ship(550,450,-3.1415,(240,100,100)),ship(550,450,-3.1415,(240,100,100))]
        newBestCount = 0
        for shp in ships:
            if(shp.score > bestship[0].score):
                bestship[2] = copy.deepcopy(bestship[1])
                bestship[1] = copy.deepcopy(bestship[0])
                bestship[0] = copy.deepcopy(shp)
                newBest = True
            elif(shp.score > bestship[1].score):
                bestship[2] = copy.deepcopy(bestship[1])
                bestship[1] = copy.deepcopy(shp)
            elif(shp.score > bestship[2].score):
                bestship[2] = copy.deepcopy(shp)
                
        for i in range(3):
            newbestsurface[i] = myfont.render("High Score: "+str(int(bestship[i].score)),  False, bestship[i].colour)
           
            
        n = 0
        print("All crashed for generation " + str(generation) +"  Top Ship score: " + str(bestship[0].score) + "  at  " + str(bestship[0].weights1[0][0]))
        generation +=1
        gencoef = 1/(generation +1) 
        for shp in ships:
            shp.reset()
            if(n == 0): shp.copyWeights(bestship[0],0, (240,240,240))
            elif(n < 10): 
                shp.copyWeights(bestship[n%3],0.000001*gencoef, (240,200,200))
            elif(n < 20): 
                shp.copyWeights(bestship[n%3],0.00001*gencoef, (240,100,100))
            elif(n < 30): 
                shp.copyWeights(bestship[n%3],0.0001*gencoef, (240,0,0))
            elif(n < 40): 
                shp.copyWeights(bestship[n%3],0.001*gencoef, (200,240,200))
            elif(n < 50): 
                shp.copyWeights(bestship[n%3],0.01*gencoef, (100,240,100))
            elif(n < 60): 
                shp.copyWeights(bestship[n%3],0.1*gencoef, (0,240,0))
            elif(n < 70): 
                shp.copyWeights(bestship[n%3],100*gencoef, (100,100,100))
            elif(n < 80): 
                shp.copyWeightsExper(bestship[n%3],0.001*gencoef, (200,200,240))
            elif(n < 90): 
                shp.copyWeightsExper(bestship[n%3],0.1*gencoef, (100,100,240))
            else: 
                shp.copyWeightsExper(bestship[n%3],10*gencoef, (0,0,240))
            shp.drawShip()
            n+=1
    if(newBest):
        for i in range(3):   
            screen.blit(newbestsurface[i],(0,50*(i+1)))
            pygame.draw.circle(screen, bestship[i].colour, [int(bestship[i].x),int(bestship[i].y)], 10,2)
            pygame.draw.circle(screen, bestship[i].colour, [int(bestship[i].x),int(bestship[i].y)], 20,2)
                
    time.tick(30)
    pygame.display.flip()