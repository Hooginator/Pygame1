#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 14 13:30:41 2018

@author: hoog
"""

from game import *

def drawWinners():
    pass


for i in range(1):
    screen = pygame.display.set_mode((1600,900))
    #playCountdown(screen)
    playGame(screen = screen, maxGen = 100, basename = "INT_0_"+str(i),intermediates = ())
quitGame()



############################################################
########## EXTRA SCREENS ###################################
############################################################

def playCountdown(screen, seconds = 5,pos = (500,400)):
    time = pygame.time.Clock()
    for t in range(seconds):
        drawBackground(screen)
        timersurface = myfont.render(str(seconds - t), False, (240,240,240))
        screen.blit(timersurface,pos,) 
        # Updates screen
        pygame.display.flip()
        # Wait for next frame time          
        time.tick(1)
