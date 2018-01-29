# -*- coding: utf-8 -*-
"""
Created on Wed Jan 24 15:08:54 2018

@author: hoog
BUG: lategame I have noticed that the top player oscillates between 2 options 
"""

import sys, pygame
import numpy as np
pygame.init()

myfont = pygame.font.SysFont('Comic Sans MS', 30)

size = width, height = 600, 600

colours = [(100,120,220),(240,120,120)]

INPUTS = 16
INTERMEDIATE = 8
OUTPUTS = 4


class ship:
    def __init__(self, x, y, angle,colour):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.drag = 0.70
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
    def updateSpeed(self,accel,dangle):
        self.angle += dangle
        self.vx += accel * np.cos(self.angle)
        self.vy += accel * np.sin(self.angle)
        self.vx = self.vx * self.drag
        self.vy = self.vy * self.drag
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
                        [int(self.x + 150*np.cos(self.angle-0.5)), int(self.y  + 150*np.sin(self.angle-0.5))],
                     [int(self.x + 150*np.cos(self.angle+0.5)), int(self.y  + 150*np.sin(self.angle+0.5))],
                      [int(self.x + 150*np.cos(self.angle-1)), int(self.y  + 150*np.sin(self.angle-1))],
                       [int(self.x + 150*np.cos(self.angle+1)), int(self.y  + 150*np.sin(self.angle+1))],
                       [int(self.x + 150*np.cos(self.angle)), int(self.y  + 150*np.sin(self.angle))],
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
    def reset(self):
        self.x = 550
        self.y = 450
        self.angle = -3.1415
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
        self.score -= getDist(checkpoints[self.checkpoint].getMid(),[self.x,self.y])
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
        self.weights1 = np.random.random((INPUTS,INTERMEDIATE))
        self.weights2 = np.random.random((INTERMEDIATE,OUTPUTS))
        self.bias1 = np.random.random((1,INTERMEDIATE))
        self.bias2 = np.random.random((1,OUTPUTS))
    def getDecision(self):
        return np.add(np.add(self.scan.dot(self.weights1), self.bias1).dot(self.weights2),self.bias2).T
    def copyWeights(self, ship, stray, colour):
        if(stray == 0):
            self.weights1 = ship.weights1
            self.weights2 = ship.weights2
            self.bias1 = ship.bias1
            self.bias2 = ship.bias2
        else:
            self.weights1 = ship.weights1 + np.random.random((INPUTS,INTERMEDIATE))*stray
            self.weights2 = ship.weights2 + np.random.random((INTERMEDIATE,OUTPUTS))*stray
            self.bias1 = ship.bias1 + np.random.random((1,INTERMEDIATE))*stray
            self.bias2 = ship.bias2 + np.random.random((1,OUTPUTS))*stray
        self.colour = colour
        
        
class wall:
    def __init__(self,posx,posy,sizex,sizey):
        self.posx = posx
        self.posy = posy
        self.sizex = sizex
        self.sizey = sizey
    def drawWall(self):
        pygame.draw.rect(screen,(0,0,255),(self.posx, self.posy, self.sizex, self.sizey))
    def checkCollision(self,x,y):
        return ((self.posx <= x) and (self.posx + self.sizex >= x) and (self.posy <= y) and (self.posy + self.sizey >= y))
    def getMid(self):
        return [self.posx + self.sizex/2,self.posy + self.sizey/2]

def checkCollisions(walls,x,y):
    for wall in walls:
        if(wall.checkCollision(x,y)): return True
    if((x < 0) or (x > width) or (y < 0) or (y > height)): return True
    return False
def drawWalls(walls):
    for wall in walls: wall.drawWall()
def getDist(pos1,pos2):
    return np.sqrt((pos1[0]-pos2[0])*(pos1[0]-pos2[0])+(pos1[1]-pos2[1])*(pos1[1]-pos2[1]))
maxangle = 0.6
maxaccel = 0.5
black = 0, 0, 0
time = pygame.time.Clock()
generation = 0

ships = [ship(550,450,-3.1415,(240,100,100)) for i in range(100)]
walls = [wall(80,100,70,350),wall(150,100,300,50),wall(150,400,200,50),wall(300,250,300,50)]
checkpoints = [wall(0,450,150,150),wall(50,0,150,150),wall(450,50,150,150),wall(150,200,150,150),wall(250,450,150,150)]
for shp in ships: shp.getInputs()
screen = pygame.display.set_mode(size)

bestship = ship(550,450,-3.1415,(240,100,100))
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
            angle -= controlInputs[0] * maxangle
            angle += controlInputs[1] * maxangle
            accel += controlInputs[2] * maxaccel
            accel -= 0.25*controlInputs[3] * maxaccel
            
            shp.updateSpeed(accel,angle) 
            shp.updatePos()
            if(checkCollisions(walls,shp.x,shp.y) or shp.timeDriving > 150* (1+shp.checkpoint + 4*shp.laps) or shp.timeDriving > 3000): shp.crash()
        shp.drawShip()
    if(allcrashed):
        for shp in ships:
            if(shp.score > bestship.score):
                print("New Best Ship Score: " + str(shp.score)+ "  at  " + str(shp.x) + "  " + str(shp.y))
                
                bestship.copyWeights(shp,0,(0,0,0))
                bestship.score = shp.score
        n = 0
        print("All crashed for generation " + str(generation) +"  Top Ship score: " + str(bestship.score) + "  at  " + str(bestship.weights1[0][0]))
        generation +=1
        for shp in ships:
            shp.reset()
            if(n == 0): shp.copyWeights(bestship,0, (240,240,240))
            elif(n < 10): 
                shp.copyWeights(bestship,0.00001, (240,100,100))
            elif(n < 30): 
                shp.copyWeights(bestship,0.0001, (240,240,100))
            elif(n < 50): 
                shp.copyWeights(bestship,0.001, (100,240,100))
            elif(n < 70): 
                shp.copyWeights(bestship,0.01, (100,240,240))
            elif(n < 90): 
                shp.copyWeights(bestship,0.1, (100,100,240))
            else: 
                shp.copyWeights(bestship,0.5, (240,100,240))
            shp.drawShip()
            n+=1
            
    time.tick(60)
    pygame.display.flip()