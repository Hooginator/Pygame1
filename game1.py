# -*- coding: utf-8 -*-
"""
Created on Wed Jan 24 15:08:54 2018

@author: hoog

"""

from functions import *
from ship import ship


# Screen constants
size = width, height = 1600, 900


        
   


############################################################
########### WALL CLASS #####################################
############################################################

     
class wall:
    """ for impassable walls and checkpoints"""
    def __init__(self,posx,posy,sizex,sizey):
        self.posx = posx
        self.posy = posy
        self.sizex = sizex
        self.sizey = sizey
    def drawWall(self):
        """ Draw rectangle in the way"""
        pygame.draw.rect(screen,(0,0,255),(self.posx, self.posy, self.sizex, self.sizey))
    def drawCheckpoint(self):
        """ Less intrusive draw for checkpoints"""
        pygame.draw.circle(screen,(255,255,255),self.getMidInt(), 20, 3)
    def checkCollision(self,pos):
        return self.checkCollision(self,pos[0],pos[1])
    def checkCollision(self,x,y):
        """ determine if position (x,y) is crashed """
        return ((self.posx <= x) and (self.posx + self.sizex >= x) and (self.posy <= y) and (self.posy + self.sizey >= y))
    def getMid(self):
        """ returns the center of the wall"""
        return [self.posx + self.sizex/2,self.posy + self.sizey/2]
    def getMidInt(self):
        """ returns the center of the wall AS AN INTEGER!!"""
        return [int(self.posx + self.sizex/2),int(self.posy + self.sizey/2)]
    def maze(i):
        """ Here is the "savefile" of my mazes or maps.  """
        if(i == 0):
            return [wall(80,100,70,350),wall(150,100,300,50),wall(150,400,200,50),wall(300,250,300,50)]
        elif(i == 1):
            return [wall(200,650,1000,50),wall(200,200,50,450),wall(400,0,50,400),wall(450,350,300,50),
                    wall(850,100,50,550),wall(600,100,250,50),wall(1000,0,50,500),wall(1200,200,50,500),
                    wall(1250,200,200,50),wall(1400,400,200,50),wall(1250,650,200,50)]
    
    def checkpoints(i):
        """ Here is the "savefile" of my checkpoints corresponding to the above maps.  """
        if(i == 0):
            return [wall(0,450,150,150),wall(50,0,150,150),wall(450,50,150,150),wall(150,200,150,150),wall(250,450,150,150)]
        elif(i == 1):
            return [wall(200,0,200,200),wall(400,400,250,250),wall(750,300,100,100),wall(450,0,200,100),wall(900,0,100,150),wall(1050,400,150,150),
            wall(1450,100,150,150),wall(1250,400,150,150),wall(1400,650,200,200),wall(0,500,200,200)]



############################################################
########## MAIN PROGRAM ####################################
############################################################
    
# Initialization     
time = pygame.time.Clock()
generation = 0
nseeds = 10

filename = "./data/BestShips"
fileext = ".txt"

ships = [ship(50,50,0,(240,100,100)) for i in range(100)]
walls = wall.maze(1)
checkpoints = wall.checkpoints(1)
checkpointPerLap = len(checkpoints)
screen = pygame.display.set_mode(size)
newbestsurface = [None]*nseeds
newBest = False
#manual = False
allcrashed = False
while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()
    screen.fill((0,0,0))
    drawWalls(walls)
    #drawWalls(checkpoints)
    
    # Once everyone has crashed / run out of fuel we restart at the next generation
    if(allcrashed):
        # Determine best ships
        ships.sort(key = lambda x: x.score, reverse = True)
        bestship = copy.deepcopy(ships[0:nseeds])
        newBest = True
        # Save top of each generation
        bestship[0].saveWeights(filename, generation)
        # Create surface for a high score table
        for i in range(min(nseeds,10)):
            newbestsurface[i] = myfont.render(str(i) + ":   " + str(int(bestship[i].score)) +"   "+bestship[i].getName(),  False, bestship[i].colour)
           
            
        n = 0
        print("All crashed for generation " + str(generation) +"  Top Ship score: " + str(bestship[0].score) + "  at  " + str(bestship[0].weights[0][0][0]))
        generation +=1
        gencoef = 1/(generation +1) 
        for shp in ships:
            if(n < 20): 
                shp.copyWeights(bestship[n%nseeds],0.1*gencoef*gencoef, (240,100,100))
            elif(n < 40): 
                shp.copyWeights(bestship[n%nseeds],0.1*gencoef, (240,240,100))
            elif(n < 60): 
                shp.copyWeights(bestship[n%nseeds],0.5*gencoef, (100,240,100))
            elif(n < 80): 
                shp.copyWeights(bestship[n%nseeds],1*gencoef, (100,240,240))
            elif(n < 90): 
                shp.initWeights()
                shp.colour = (100,100,240)
            elif(n < 1000): 
                shp.copyWeightsExper(bestship[n%nseeds],1*gencoef, (240,100,240))
            n+=1
            shp.reset()
    # Move
    allcrashed = True
    for shp in ships:
        if(shp.crashed == False):
            shp.moveShip(checkpoints)
            if(checkCollisions(walls,[shp.x,shp.y],width,height) or shp.checkFuel(len(checkpoints)) < 0):
                shp.crash(checkpoints)
            if(allcrashed): # The first one we find not crashed
                shp.drawMatrix(screen)
                shp.highlight(screen)
                allcrashed = False
        shp.drawShip(screen,walls,width,height)
    if(newBest):
        for i in range(min(nseeds,10)):   
            screen.blit(newbestsurface[i],(0,50*(i+4)))
            pygame.draw.circle(screen, bestship[i].colour, [int(bestship[i].x),int(bestship[i].y)], 10,2)
            pygame.draw.circle(screen, bestship[i].colour, [int(bestship[i].x),int(bestship[i].y)], 20,2)
    
    textsurface = myfont.render("Gen: "+str(generation), False, (240, 240, 240))
    screen.blit(textsurface,(0,0))   
    # TESTING FOR OBS VIDEO 2
    #if(generation > 1):
    #    os.system("shutdown now")            
    time.tick(30)
    pygame.display.flip()
