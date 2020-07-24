#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 15 18:31:57 2018

@author: hoog
"""

from functions import *

class hud:
    """ Heads Up Display class to manage all the addons """
    def __init__(self, generation = 0,nseeds = 10, basepos = (0,200),maze = None,
                 victoryLap = False,description = None):
        self.gen = generation
        self.leadship = None
        self.nseeds = nseeds
        self.frame = 0
        self.genStartFrame = 0
        self.checkpoint = 0
        self.lastCheckpointCost = 0
        self.nextCheckpointCost = 0
        self.basepos = basepos
        self.winnerSurface = None
        self.genSurface = None
        self.winnerPos =None
        self.winnerColour = []
        self.maze = maze
        self.victoryLap = victoryLap
        self.description = description
        self.updateGeneration(generation)
        
    def update(self,screen,generation, frame,bestships = None,ships = None,drawLeaderboard = False,
               leadship = None, camerapos = None,followLead = False, drawMatrix = False,
               highlightWinners = True):
        """general update function that calls all the other pieces"""
        self.frame = frame
        if camerapos is not None:
            midpos = camerapos
        else:
            midpos = (800,450)
        if(generation > self.gen or frame == 0): 
            self.updateGeneration(generation)
            self.updateWinners(bestships,generation)
        if (highlightWinners and self.winnerPos is not None): 
            self.highlightWinners(screen,frame,midpos = midpos)
        if(drawLeaderboard and self.winnerSurface is not None): 
            self.drawBackground(screen)
            self.drawLeaderNames(screen,midpos = midpos)
        if(leadship is not None and drawMatrix):
            leadship.drawMatrix(screen,[self.basepos[0] + 70,self.basepos[1] + 450])
            leadship.highlight(screen,midpos = midpos)
        if(self.victoryLap):
            pass
        else:
            self.drawGeneration(screen)
        self.drawTimer(screen)
        # Also draw the indicator for current checkpoint
        self.maze.drawCheckpoint(screen,self.checkpoint,self.frame,midpos = midpos)
        return
    def updateWinners(self,bestships,generation):
        """ Updates / creates the list of names of the winners of the last 
        generation that will be displayed """
        self.winnerSurface = []
        self.winnerPos = []
        self.winnerColour = []
        self.winnerSurface.append(myfont.render("GEN "+str(self.gen-1)+ " BEST",False, (250,250,250)))
        for i, shp in enumerate(bestships):
            tempSurf = myfont.render(str(i) + ":   " + str(int(shp.score)) 
                                    +"   "+shp.getName(),  False, shp.colour)
            self.winnerSurface.append(tempSurf)
            self.winnerPos.append(shp.getIntPos())
            self.winnerColour.append(shp.colour)
            
    def drawTimer(self,screen):
        """ Creates and places the small pulsing timer that rotates each time 
        another checkpoint has expired """
        if(self.frame - self.genStartFrame >= self.nextCheckpointCost):
            self.checkpoint +=1
            self.lastCheckpointCost = self.nextCheckpointCost
            self.nextCheckpointCost = self.maze.checkFuelCost(self.checkpoint)
        angle = 2*np.pi*(self.nextCheckpointCost - self.frame + self.genStartFrame) / (self.nextCheckpointCost - self.lastCheckpointCost)
        temppos = [50 - 20*np.sin(angle),50 - 20*np.cos(angle)]
        tempsize = int(angle * 3)
        pygame.draw.line(screen,(240,240,240),(50,50),temppos,2)
        pygame.draw.circle(screen,(240,240,240),(50,50),max(24-tempsize,1),1)
        
        

    def drawLeaderNames(self,screen,midpos = (800,450)):
        """ Draws a list of the last generation's top 10 performers with their
        scores """
        for i, surf in enumerate(self.winnerSurface):
            screen.blit(surf,(self.basepos[0]+6,self.basepos[1]+30*i))
            
    def highlightWinners(self,screen,frame,midpos = (800,450)):
        """ Draws circles around where the last generations lead ships ended up"""
        for i, pos in enumerate(self.winnerPos):
            
            if i > self.nseeds-1:
                break
            drawPulsatingCirlce(screen,getOffsetPos(pos,midpos),frame,colour = self.winnerColour[i],size = 20,cycle_length = 60,magnitude = 0.8,reverse_alpha = True)
        
            #pygame.draw.circle(screen, self.winnerColour[i], getOffsetPos(pos,midpos), 10,2)
            #pygame.draw.circle(screen, self.winnerColour[i], getOffsetPos(pos,midpos), 20,2)
        
    def updateGeneration(self,generation):
        """ Everything the HUD needs to do after a generation has ended """
        self.gen = generation
        self.genStartFrame = self.frame
        self.checkpoint = 0
        self.lastCheckpointCost = 0
        self.nextCheckpointCost = self.maze.checkFuelCost(self.checkpoint)
        if self.description == None:
            self.genSurface = myfont.render("Gen: "+str(self.gen), False, (240, 240, 240))
        else:
            self.genSurface = myfont.render(self.description+"    Gen: "+str(self.gen) , False, (240, 240, 240))
        
    def drawGeneration(self,screen):
        """ Draw surface that shows the generation number in the top left corner """
        screen.blit(self.genSurface,(0,0)) 
        
    def drawBackground(self,screen):      
        """ Draw a black background for the leaderboard """
        pygame.draw.rect(screen,(240,240,240),(self.basepos[0],self.basepos[1],204,504))
        pygame.draw.rect(screen,(0,0,0),(self.basepos[0]+2,self.basepos[1]+2,200,500))