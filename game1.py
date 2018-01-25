# -*- coding: utf-8 -*-
"""
Created on Wed Jan 24 15:08:54 2018

@author: hoog
"""

import sys, pygame
pygame.init()


class ship:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.angle = angle

def moveTowards(tomove, target, speed):
    toreturn = tomove
    if(tomove[0] > target[0]):
        toreturn[0] = - speed[0]
    else: toreturn[0] = speed[0]
    
    if(tomove[1] > target[1]):
        toreturn[1] = - speed[1]
    else: toreturn[1] = speed[1]
    return toreturn
    
def rotateCenter(image, rect, angle):
    new_image = pygame.transform.rotate(image, angle)
    # Get a new rect with the center of the old rect.
    rect = new_image.get_rect(center=rect.center)
    return new_image, rect


size = width, height = 620, 440
speed = [5, 2]
black = 0, 0, 0
time = pygame.time.Clock()

ship1 = ship(2,2,2)

screen = pygame.display.set_mode(size)

ball = pygame.image.load("ship.png")
ballrect = ball.get_rect()

x,y = 100,100

while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()
            
    key = pygame.key.get_pressed()
    pos = ballrect
    if key[pygame.K_a] or key[pygame.K_LEFT]:
        ball,ballrect = rotateCenter(ball,ballrect, 2)
    if key[pygame.K_d] or key[pygame.K_RIGHT]:
        ball,ballrect = rotateCenter(ball,ballrect, -2)
        #if event.type == pygame.KEYDOWN:
        #    if key[pygame.K_a] or key[pygame.K_LEFT]:
        #         ball = pygame.transform.rotate(ball, 2)

    #ballrect = ballrect.move(moveTowards(list(ballrect.center),pygame.mouse.get_pos(), speed))

    screen.fill(black)
    screen.blit(ball, ballrect)
    triangle = pygame.draw.polygon(screen, (240,70,80), [[x, y], [x -10, y -20], [x + 10, y - 20]], 2)
    triangle = pygame.draw.circle(screen, (140,160,240), [x, y-10], 5,2)
    time.tick(30)
    pygame.display.flip()