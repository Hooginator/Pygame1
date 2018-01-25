# -*- coding: utf-8 -*-
"""
Created on Wed Jan 24 15:08:54 2018

@author: hoog
"""

import sys, pygame
pygame.init()


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
speed = [5, 2]
black = 0, 0, 0
time = pygame.time.Clock()

screen = pygame.display.set_mode(size)

ball = pygame.image.load("ball.bmp")
ballrect = ball.get_rect()

while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()
        
        if event.type == pygame.KEYDOWN:
            key = pygame.key.get_pressed()
            if key[pygame.K_a] or key[pygame.K_LEFT]:
                speed = [50, 20]

    ballrect = ballrect.move(moveTowards(list(ballrect.center),pygame.mouse.get_pos(), speed))

    screen.fill(black)
    screen.blit(ball, ballrect)
    time.tick(30)
    pygame.display.flip()