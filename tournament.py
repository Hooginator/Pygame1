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
        
        
def victoryLap(screen, basename, nships = 10):
    """ Loads previous winners instead of random ships """
    playGame(screen = screen, maxGen = 1, basename = basename,
             victoryLap = True,nships = nships, displayHUD = False, shipLoadOffset = 0)

def getFilename(base, inangles, indistances,intermediates):
    temp =  base + "_" + str(len(inangles)) + "x"+str(len(indistances))
    for inter in intermediates:
        temp = temp +"_"+str(inter)
    return temp

############################################################
########## TOURNAMENT ## ###################################
############################################################

inputangles = [[0.8,0.4,0,-0.4,-0.8]]
inputdistances = [[50,100,150]]
intermediates = [(6,6,),(8,6,),(10,6,),(12,6,),(14,6,)]

winningShip = None
i = 1
for ina in inputangles:
    for ind in inputdistances:
        for inter in intermediates:
            filename = getFilename("teeeestinggg",ina,ind,inter)
            screen = pygame.display.set_mode((1600,900))
            playCountdown(screen,winningShip = winningShip)
            #winningShip = playGame(screen = screen, maxGen = 100, basename = filename, 
            #                       intermediates = inter,inputdistance = ind, 
            #                       inputangle = ina, nships = 100, nseeds = 20)
            victoryLap(screen,basename = filename,nships = 3)
            i += 1
quitGame()
#os.system("shutdown now -h")



