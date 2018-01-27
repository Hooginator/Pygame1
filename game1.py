# -*- coding: utf-8 -*-
"""
Created on Wed Jan 24 15:08:54 2018

@author: hoog
"""

import sys, pygame
import numpy as np
pygame.init()


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
        if(self.vx*self.vx + self.vy*self.vy > self.maxSpeed):
            self.vx = self.vx *0.9
            self.vy = self.vy *0.9
    def updatePos(self):
        self.x += self.vx
        self.y += self.vy
def moveTowards(tomove, target, speed):
    toreturn = tomove
    if(tomove[0] > target[0]):
        toreturn[0] = - speed[0]
    else: toreturn[0] = speed[0]
    
    if(tomove[1] > target[1]):
        toreturn[1] = - speed[1]
    else: toreturn[1] = speed[1]
    return toreturn



size = width, height = 620, 440
accel = [2,2]
maxspeed = [5, 5]
black = 0, 0, 0
time = pygame.time.Clock()

ship1 = ship(2,2,2)

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
       angle += 1
    if key[pygame.K_d] or key[pygame.K_RIGHT]:
       angle -= 1
    if key[pygame.K_w] or key[pygame.K_UP]:
       accel = 2
    if key[pygame.K_s] or key[pygame.K_DOWN]:
       accel = -2
    if key[pygame.K_SPACE]:
        accel = 0
    
    # Move
    ship1.updateSpeed(accel,angle) 
    ship1.updatePos()
    screen.fill(black)
    x,y = int(ship1.x), int(ship1.y)
    triangle = pygame.draw.polygon(screen, (240,70,80), [[x, y], [x -10, y -20], [x + 10, y - 20]], 2)
    triangle = pygame.draw.circle(screen, (140,160,240), [x, y-10], 5,2)
    time.tick(30)
    pygame.display.flip()