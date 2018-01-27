# -*- coding: utf-8 -*-
"""
Created on Wed Jan 24 15:08:54 2018

@author: hoog
"""

import sys, pygame
import numpy as np
pygame.init()

size = width, height = 620, 440

class ship:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.maxSpeed = 10
        self.angle = angle
    def updateSpeed(self,accel,dangle):
        self.angle += dangle
        self.vx += accel * np.cos(self.angle)
        self.vy += accel * np.sin(self.angle)
        if(self.vx > self.maxSpeed): self.vx = self.maxSpeed
        if(self.vy > self.maxSpeed): self.vy = self.maxSpeed
    def updatePos(self):
        self.x += self.vx
        self.y += self.vy
        self.x = max(self.x,0)
        self.y = max(self.y,0)
        self.x = min(self.x,width)
        self.y = min(self.y,height)
def moveTowards(tomove, target, speed):
    toreturn = tomove
    if(tomove[0] > target[0]):
        toreturn[0] = - speed[0]
    else: toreturn[0] = speed[0]
    
    if(tomove[1] > target[1]):
        toreturn[1] = - speed[1]
    else: toreturn[1] = speed[1]
    return toreturn



accel = [2,2]
maxangle = 0.04
maxaccel = 0.5
black = 0, 0, 0
time = pygame.time.Clock()

ship1 = ship(200,200,2)

screen = pygame.display.set_mode(size)

x,y = 100,100
speed = [0,0]
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
       accel = -maxaccel
    if key[pygame.K_SPACE]:
        accel = 0
    
    # Move
    ship1.updateSpeed(accel,angle) 
    ship1.updatePos()
    screen.fill(black)
    x,y,angle = int(ship1.x), int(ship1.y), ship1.angle
    triangle = pygame.draw.polygon(screen, (240,70,80), [[int(x+ 10 *np.cos(angle)), int(y+ 10 *np.sin(angle))],
                                   [int(x+ 10 *np.cos(angle + 2)), int(y+ 10 *np.sin(angle + 2))],
                                   [int(x+ 10 *np.cos(angle + 4)), int(y+ 10 *np.sin(angle + 4))]])
    triangle = pygame.draw.circle(screen, (140,160,240), [x, y], 5,2)
    time.tick(30)
    pygame.display.flip()