#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 15 18:31:57 2018

@author: hoog
"""

from functions import *

class hud:
    """ Heads Up Display class to manage all the addons """
    def __init__(self, generation = 0,nseeds = 10, basepos = (0,200)):
        self.gen = generation
        self.leadship = None
        self.nseeds = nseeds
        self.frame = 0
        self.basepos = basepos
    def updateWinners(self,bestships):
        """ Updates / creates the list of names of the winners of the last 
        generation that will be displayed """
        self.winnerSurface = []
        self.winnerPos = []
        self.winnerSurface.append(myfont.render("GEN "+str(self.gen-1)+ " WINNERS",False, (250,250,250)))
        for i, shp in enumerate(bestships):
            self.winnerSurface.append(myfont.render(str(i) + ":   " + str(int(shp.score)) +"   "+shp.getName(),  False, shp.colour))
            self.winnerPos.append(shp.pos)