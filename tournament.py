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
        
        
def victoryLap(basenames, nships = 5, gen = 70):
    """ Loads previous winners for show instead of random ships  """
    screen = pygame.display.set_mode((1600,900))
    playGame(screen = screen, maxGen = 100, basename = basenames[0],
             victoryLap = True,victoryLapShipsPerGen = nships, displayHUD = False, victoryLapGen = gen,
             victoryLapNames = basenames)

def getFilename(base, inangles, indistances,intermediates):
    temp =  base + "_" + str(len(inangles)) + "x"+str(len(indistances))
    for inter in intermediates:
        temp = temp +"_"+str(inter)
    return temp

############################################################
########## TOURNAMENT ## ###################################
############################################################

def doTournament(filePrefix = "Test",inputangles = [[0.8,0.4,0.2,0.1,0,-0.1,-0.2,-0.4,-0.8]], inputdistances = [[50,100,150,200]], 
                 intermediates = [[]], shutdown = False, orders = [1,2,3,4,5]):
    """ Command to actually run the simulation to get more new racers after 
    the specified number of generations have passed.
    """
    winningShip = None
    i = 1
    for ina in inputangles:
        for ind in inputdistances:
            for inter in intermediates:
                filename = getFilename(filePrefix,ina,ind,inter)
                
                screen = pygame.display.set_mode((1600,900))
                playCountdown(screen,winningShip = winningShip)
                winningShip = playGame(screen = screen, maxGen = 20, basename = filename, 
                                   intermediates = inter,inputdistance = ind, 
                                   inputangle = ina, nships = 40, nseeds = 8,orders = orders)
                i += 1
    if(shutdown): os.system("shutdown now -h")
    #quitGame()


def doSet():
    """ Do series of tournaments to generate a bunch of data.
    This should be little more than a simple loop
    """
    ords = []
    for j in range(5):
        ords.append(j+1)
        for i in range(10):
            if i==0:
                tempinter = [[]]
            else:
                tempinter = [[i]] 
            doTournament(filePrefix = "Nov24_Overnight_Comparison_Intermediates_"+str(i) + "_Orders_"+str(j+1),intermediates = tempinter,orders = ords)
        
        
        
        
if __name__ == "__main__":
    
    doSet()
#victoryLap(["INPUTANG04DIS50_3x3","INPUTANG04DIS50_5x3","INPUTANG04DIS50_7x3"])
