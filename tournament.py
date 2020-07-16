#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 14 13:30:41 2018

@author: hoog
"""


# todo
# BEZIER CURVE WALLS (MAYBE LATER)
# FIX TOURNAMENT FUNCTIONS TO WORK FOR LIVESTREAM SETTING
# FIGURE OUT HOW TO SCRAPE FOR DONATIONS
# -> NAME SHIPS, SHOW OFF NAME AND MAYBE LET IT LIVE? ONLY IF #1 W/ VERY LIGHT MUTATIONS?
# LET ANGLES OF SENSORS BE EVOLVED?
# pretty up countdown

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

def getFilename(base, inangles, intermediates,orders):
    temp =  base + "_ANG_" + str(len(inangles))
    temp=temp+"_INT"
    for inter in intermediates:
        temp = temp +"_"+str(inter)
    temp=temp+"_ORD"
    for ord in orders:
        temp = temp +"_"+str(ord)
    return temp + ".txt"

############################################################
########## TOURNAMENT ## ###################################
############################################################

def doTournament(filePrefix = "Test",inputangles = [0.8,0.6,0.4,0.2,0,-0.2,-0.4,-0.6,-0.8], inputdistances = [50,100,150,200], 
                 intermediates = [10], shutdown = True, orders = [1,2,3,4,5],nships=10,nseeds=1):
    """ Command to actually run the simulation to get more new racers after 
    the specified number of generations have passed.
    """
    winningShip = None
    filename = getFilename(filePrefix,inputangles,intermediates,orders)
    
    #screen = pygame.display.set_mode((1600,900))
    #playCountdown(screen,winningShip = winningShip)
    winningShip = playGame(maxGen = 200, basename = filename, play_countdown=True,
                       intermediates = intermediates,inputdistance = inputdistances, 
                       inputangle = inputangles, nships = nships, nseeds = nseeds,orders = orders)
    i += 1
    if(shutdown): os.system("shutdown now -h") # Not working on windoows
    #quitGame()


def doSet():
    """ Do series of tournaments to generate a bunch of data.
    This should be little more than a simple loop
    """
    
    # i = 1
    # for ina in inputangles:
        # for ind in inputdistances:
            # for inter in intermediates:
    
    ords = [1]
    for j in range(200):
        #ords.append(j+1)
        # for i in range(10):
            # if i==0:
                # tempinter = [[]]
            # else:
                # tempinter = [[i]] 
        doTournament(filePrefix = "DEC12_10ships_1evolution_"+str(j+1),orders = ords)
        
        
        
        
if __name__ == "__main__":
    
    doSet()
#victoryLap(["INPUTANG04DIS50_3x3","INPUTANG04DIS50_5x3","INPUTANG04DIS50_7x3"])
