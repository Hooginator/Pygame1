#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 15 18:31:57 2018

@author: hoog
"""

from functions import *

class hud:
    """ Heads Up Display class to manage all the addons """
    def __init__(self, generation = 0,nseeds = 10, basepos = (0,200),maze = None):
        self.gen = generation
        self.leadship = None
        self.nseeds = nseeds
        self.frame = 0
        self.genStartFrame = 0
        self.checkpoint = 0
        self.lastCheckpointCost = 0
        self.nextCheckpointCost = 0
        self.basepos = basepos
        self.winnerSurface = []
        self.genSurface = None
        self.winnerPos = []
        self.winnerColour = []
        self.updateGeneration(generation)
        self.maze = maze
    def update(self,screen,generation, frame,bestships = None,ships = None):
        """general update function"""
        self.frame = frame
        if(generation > self.gen or frame == 0): 
            self.updateGeneration(generation)
            self.updateWinners(bestships,generation)
        if((frame % 10 == 0) and (ships is not None)):
            self.leadship = [max(ships, key = lambda x : x.getScore()*(1-int(x.crashed)))]
        if(self.leadship is not None):
            self.drawBackground(screen)
            self.leadship[0].drawMatrix(screen,[self.basepos[0] + 70,self.basepos[1] + 440])
            self.leadship[0].highlight(screen)
        self.drawWinners(screen)
        self.drawGeneration(screen)
        self.drawTimer(screen)
            
    def updateWinners(self,bestships,generation):
        """ Updates / creates the list of names of the winners of the last 
        generation that will be displayed """
        self.winnerSurface = []
        self.winnerPos = []
        self.winnerColour = []
        self.winnerSurface.append(myfont.render("GEN "+str(self.gen-1)+ " WINNERS",False, (250,250,250)))
        for i, shp in enumerate(bestships):
            self.winnerSurface.append(myfont.render(str(i) + ":   " + str(int(shp.score)) +"   "+shp.getName(),  False, shp.colour))
            self.winnerPos.append(shp.getIntPos())
            self.winnerColour.append(shp.colour)
    def drawTimer(self,screen):
        if(self.frame - self.genStartFrame >= self.nextCheckpointCost):
            self.checkpoint +=1
            self.lastCheckpointCost = self.nextCheckpointCost
            self.nextCheckpointCost = self.maze.checkFuelCost(self.checkpoint)
        angle = 2*np.pi*(self.nextCheckpointCost - self.frame + self.genStartFrame) / (self.nextCheckpointCost - self.lastCheckpointCost)
        temppos = [50 - 20*np.sin(angle),50 - 20*np.cos(angle)]
        tempsize = int(angle * 3)
        pygame.draw.line(screen,(240,240,240),(50,50),temppos,2)
        pygame.draw.circle(screen,(240,240,240),(50,50),max(24-tempsize,1),1)
    def drawWinners(self,screen):
        for i, surf in enumerate(self.winnerSurface):
            screen.blit(surf,(self.basepos[0]+5,self.basepos[1]+30*i))
        for i, pos in enumerate(self.winnerPos):
            pygame.draw.circle(screen, self.winnerColour[i], pos, 10,2)
            pygame.draw.circle(screen, self.winnerColour[i], pos, 20,2)
    def updateGeneration(self,generation):
        self.gen = generation
        self.genStartFrame = self.frame
        self.checkpoint = 0
        self.lastCheckpointCost = 0
        self.nextCheckpointCost = 0
        self.genSurface = myfont.render("Gen: "+str(self.gen), False, (240, 240, 240))
    def drawGeneration(self,screen):
        screen.blit(self.genSurface,(0,0)) 
    def drawBackground(self,screen):        
        pygame.draw.rect(screen,(0,0,0),(self.basepos[0],self.basepos[1],200,500))