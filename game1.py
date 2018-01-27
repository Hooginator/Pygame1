# -*- coding: utf-8 -*-
"""
Created on Wed Jan 24 15:08:54 2018

@author: hoog
"""

import sys, pygame
import numpy as np
pygame.init()

size = width, height = 620, 440

colours = [(100,120,220),(240,120,120)]


class ship:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.drag = 0.96
        self.angle = angle
        self.crashed = False
        self.score = 0
        self.inputColour = [colours[0],colours[0],colours[0],colours[0]]
    def updateSpeed(self,accel,dangle):
        self.angle += dangle
        self.vx += accel * np.cos(self.angle)
        self.vy += accel * np.sin(self.angle)
        self.vx = self.vx * self.drag
        self.vy = self.vy * self.drag
    def updatePos(self):
        self.x += self.vx
        self.y += self.vy
        self.score += np.sqrt(self.vx*self.vx + self.vy*self.vy)
        if((self.x < 0) or (self.x > width) or (self.y < 0) or (self.y > height)): self.crash()
    def getInputs(self):
        self.inputPos = [[int(self.x + 40*np.cos(self.angle-0.5)), int(self.y  + 40*np.sin(self.angle-0.5))],
                     [int(self.x + 40*np.cos(self.angle+0.5)), int(self.y  + 40*np.sin(self.angle+0.5))],
                      [int(self.x + 40*np.cos(self.angle-1)), int(self.y  + 40*np.sin(self.angle-1))],
                       [int(self.x + 40*np.cos(self.angle+1)), int(self.y  + 40*np.sin(self.angle+1))]]
        i = 0
        for pos in self.inputPos:
            if(wall1.checkCollision(pos[0],pos[1])): 
                self.inputColour[i] = colours[1]
            else: self.inputColour[i] = colours[0]
            i += 1
                       
    def drawShip(self):
        pygame.draw.polygon(screen, (240,70,80), [[int(self.x+ 10 *np.cos(self.angle)), int(self.y+ 10 *np.sin(self.angle))],
                                   [int(self.x+ 10 *np.cos(self.angle + 2.64)), int(self.y+ 10 *np.sin(self.angle + 2.64))],
                                   [int(self.x+ 10 *np.cos(self.angle + 3.64)), int(self.y+ 10 *np.sin(self.angle + 3.64))]])
        self.getInputs()
        pygame.draw.circle(screen, self.inputColour[0], self.inputPos[0], 4,1)
        pygame.draw.circle(screen, self.inputColour[1], self.inputPos[1], 4,1)
        pygame.draw.circle(screen, self.inputColour[2], self.inputPos[2], 4,1)
        pygame.draw.circle(screen, self.inputColour[3], self.inputPos[3], 4,1)
        pygame.draw.circle(screen, (140,160,240), [int(self.x), int(self.y)], 5,2)
    def crash(self):
        self.crashed = True
        self.vx = 0
        self.vy = 0
        print("You crashed, score: " + str(self.score))
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

maxangle = 0.08
maxaccel = 0.8
black = 0, 0, 0
time = pygame.time.Clock()

ship1 = ship(50,50,0)
wall1 = wall(200,190,100,50)
ship1.getInputs()
screen = pygame.display.set_mode(size)

x,y = 100,100
while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()
    angle = 0
    accel = 0        
    key = pygame.key.get_pressed()
    if key[pygame.K_a] or key[pygame.K_LEFT]:
       angle -= maxangle
    if key[pygame.K_d] or key[pygame.K_RIGHT]:
       angle += maxangle
    if key[pygame.K_w] or key[pygame.K_UP]:
       accel = maxaccel
    if key[pygame.K_s] or key[pygame.K_DOWN]:
       accel = -0.5*maxaccel
    if key[pygame.K_SPACE]:
        accel = 0
    
    # Move
    if(ship1.crashed == False):
        ship1.updateSpeed(accel,angle) 
        ship1.updatePos()
        if(wall1.checkCollision(ship1.x,ship1.y)): ship1.crash()
    screen.fill(black)
    wall1.drawWall()
    ship1.drawShip()
    time.tick(30)
    pygame.display.flip()