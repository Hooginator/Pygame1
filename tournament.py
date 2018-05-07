#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 14 13:30:41 2018

@author: hoog
"""

from game import *

def drawWinners():
    pass

############################################################
########## EXTRA SCREENS ###################################
############################################################

def playCountdown(screen, seconds = 1,pos = (500,400),winningShip = None):
    winsurface = []
    if winningShip is not None:
        winsurface.append(myfont.render("Top Scorer:  ", False,(240,240,240)))
        winsurface.append(myfont.render(winningShip[0].getName() + " " 
                  + str(int(winningShip[0].score)), False, winningShip[0].colour))
    
    time = pygame.time.Clock()
    for t in range(seconds):
        drawBackground(screen)
        if winningShip is not None:
            dist = 0
            for wn in winsurface:
                screen.blit(wn,(pos[0]-40+dist,pos[1]-100)) 
                dist += wn.get_width()
        timersurface = myfont.render("Next race starting in ... " 
                                     + str(seconds - t), False, (240,240,240))
        screen.blit(timersurface,pos) 
        # Updates screen
        pygame.display.flip()
        # Wait for next frame time          
        time.tick(1)
        
        
def victoryLap(screen,basename,gens = 10, inputdistance = [50,100,150], inputangle = [1.2,0.6,0,-0.6,-1.2]):
    playGame(screen = screen, maxGen = 1, basename = basename,intermediates = (),
             victoryLap = True,nships = gens, inputdistance = inputdistance,
             inputangle = inputangle)





############################################################
########## TOURNAMENT ## ###################################
############################################################

inputangles = [[0.8,-0.8],[1,0.4,-0.4,-1],[1.2,0.6,0.2,-0.2,-0.6,-1.2]]
inputdistances = [[50,],[50,100],[50,100,150]]


winningShip = None
i = 0
for ina in inputangles:
    for ind in inputdistances:
        screen = pygame.display.set_mode((1600,900))
        playCountdown(screen,winningShip = winningShip)
        winningShip = playGame(screen = screen, maxGen = 100, basename = "TEEEST" 
                + str(i),intermediates = (),inputdistance = ind, 
                inputangle = ina)
        victoryLap(screen,basename = "TEEEST"+ str(i),gens = 20,inputdistance = ind, 
                inputangle = ina)
        i += 1
quitGame()




