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
from datetime import date as dt
import itertools
import random

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

def getFilename(base, inangles, intermediates,orders,date = False):
    """ Puts together a filename based on various parameters"""
    temp =  base + "_ANG_" + str(len(inangles))
    temp=temp+"_INT"
    for inter in intermediates:
        temp = temp +"_"+str(inter)
    temp=temp+"_ORD"
    for ord in orders:
        temp = temp +"_"+str(ord) +"_"
    temp = temp + str(dt.today())
    return temp 

############################################################
########## TOURNAMENT ## ###################################
############################################################

def doTournament(filePrefix = "Test",inputangles = [0.8,0.6,0.4,0.2,0,-0.2,-0.4,-0.6,-0.8], inputdistances = [50,100,150,200], 
                 intermediates = [10],  orders = [1,2,3,4,5],nships=20,nseeds=5,description = "MatrixRacer"):
    """ Command to actually run the simulation to get more new racers after 
    the specified number of generations have passed.
    """
    winningShip = None
    filename = getFilename(filePrefix,inputangles,intermediates,orders)
    
    #screen = pygame.display.set_mode((1600,900))
    #playCountdown(screen,winningShip = winningShip)
    winningShip = playGame(maxGen = 100, basename = filename, play_countdown=True,
                       intermediates = intermediates,inputdistance = inputdistances, 
                       inputangle = inputangles, nships = nships, nseeds = nseeds,orders = orders,
                       description = description)
    #quitGame()


def doSet():
    """ Do series of tournaments to generate a bunch of data.
    This should be little more than a simple loop
    """
    # List of parameters to loop over, these will be lists of the parameters to use, which are also lists
    angle_set = [[1,0.8,0.6,0.4,0.2,0,-0.2,-0.4,-0.6,-0.8,-1],
    [0.8,0.6,0.4,0.2,0,-0.2,-0.4,-0.6,-0.8],
    [0.6,0.4,0.2,0,-0.2,-0.4,-0.6],
    [0.4,0.2,0,-0.2,-0.4],
    [0.2,0,-0.2],
    [0.1,-0.1],
    [0.3,0.1,-0.1,-0.3],
    [0.5,0.3,0.1,-0.1,-0.3,-0.5],
    [0.7,0.5,0.3,0.1,-0.1,-0.3,-0.5,-0.7],
    [0.9,0.7,0.5,0.3,0.1,-0.1,-0.3,-0.5,-0.7,-0.9]]
    
    intermediates_set = [[4],[8],[12],[16],[20],
    [8,4],[12,4],[12,8],[16,4],[16,8],[16,12],[20,4],[20,8],[20,12],[20,16],
    [12,8,4],[16,8,4],[16,12,8],[20,8,4],[20,12,8],[20,12,4],[20,16,4],[20,16,8],[20,16,12],
    [16,12,8,4],[20,16,12,4],[20,16,8,4],[20,12,8,4],
    [20,16,12,8,4]
    ]
    orders_set = [[1],[1,2],[1,2,3],[1,2,3,4],[1,2,3,4,5],[1,2,3,4,5,6]]
    
    # Create options and shuffle
    temp_list = [angle_set,intermediates_set,orders_set]
    options_set = list(itertools.product(*temp_list))
    print("Going to do "+str(len(options_set))+" tournaments")
    random.shuffle(options_set)
    
    # Loop through shuffled options in order
    j = 1
    for o in options_set:
        doTournament(filePrefix = "LOLOLOLOLTEEEST"+str(j+1)+"_",orders = o[2],inputangles = o[0],intermediates = o[1],
                description = "SENSORS:: Number: "+str(len(o[0])) + " Quality: "+str(len(o[2])) +"   BRAIN:: Size: "+str(max(o[1])) + " Depth: "  + str(len(o[1])))
        j +=1
    
    # Old way that is not randomized
    # j = 1
    # for inang in angle_set:
        # for inter in intermediates_set:
            # for order in orders_set:
                # #print(inang,inter,order)
                # doTournament(filePrefix = "LOLOLOLOLTEEEST"+str(j+1)+"_",orders = order,inputangles = inang,intermediates = inter,
                # description = "Sensors Number: "+str(len(inang)) + " Quality: "+str(len(order)) +" Brain Size: "+str(max(inter)) + " Depth: "  + str(len(inter)))
                # j +=1
    

        
        
        
        
if __name__ == "__main__":
    
    doSet()
#victoryLap(["INPUTANG04DIS50_3x3","INPUTANG04DIS50_5x3","INPUTANG04DIS50_7x3"])
