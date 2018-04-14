# -*- coding: utf-8 -*-
"""
Created on Wed Jan 24 15:08:54 2018

@author: hoog

"""
# Imports the other classes and abse functions
from functions import *
from ship import *
from wall import *

############################################################
########## FUNCTIONS #######################################
############################################################

    
def drawHUD(screen,bestship,leadship,ships,nseeds,generation,newBest,frame,checkpoints):
    """ General function that will call all the smaller HUD pieces """
    bp = [0,200]
    if(newBest): drawLeaderboard(screen,bestship,nseeds,bp)
    #drawCurrentLeaders(screen,ships,nseeds,[0,150])
    leadship = max(ships, key = lambda x : x.getScore()*(1-int(x.crashed)))
    leadship.drawMatrix(screen,[bp[0] + 70,bp[1] + 450])
    leadship.highlight(screen)
        
    textsurface = myfont.render("Gen: "+str(generation), False, (240, 240, 240))
    screen.blit(textsurface,(0,0))  
def drawCurrentLeaders(screen,ships,nseeds,pos):
    """ Creates a list of who currently hjas the best score and displays that list. """
    currentLeaders = getBestShip(ships,10)
    drawLeaderboard(screen,currentLeaders,10,pos)
def drawLeaderboard(screen,bestship,nseeds,pos):
    """ Displays a list of the top scoring ships in bestship """
    pygame.draw.rect(screen,(0,0,0),(pos[0],pos[1],200,500))
    newbestsurface = myfont.render(" LEADERBOARD",False, (250,250,250))
    screen.blit(newbestsurface,(pos[0]+10,pos[1]))
    for i in range(min(nseeds,10)):
        newbestsurface = myfont.render(str(i) + ":   " + str(int(bestship[i].score)) +"   "+bestship[i].getName(),  False, bestship[i].colour)
        screen.blit(newbestsurface,(pos[0]+4,pos[1] + 30*i + 50))
        pygame.draw.circle(screen, bestship[i].colour, [int(bestship[i].x),int(bestship[i].y)], 10,2)
        pygame.draw.circle(screen, bestship[i].colour, [int(bestship[i].x),int(bestship[i].y)], 20,2)

def getBestShip(ships,nseeds):
    """ Determine and return best ships """
    ships.sort(key = lambda x: x.score, reverse = True)
    return  copy.deepcopy(ships[0:nseeds])
    
def copyShips(ships,bestship,nseeds,generation):
    """ Do the inter-generation copying of the best ships from the previous gen """
    gencoef = 1/(generation +1) 
    n = 0
    for shp in ships:
        if(n < 20): 
            shp.copyWeights(bestship[n%nseeds],stray = 0.1*gencoef*gencoef, colour = (240,100,100))
        elif(n < 40): 
            shp.copyWeights(bestship[n%nseeds],stray = 0.1*gencoef, colour = (240,240,100))
        elif(n < 60): 
            shp.copyWeights(bestship[n%nseeds],stray = 0.5*gencoef, colour = (100,240,100))
        elif(n < 80): 
            shp.copyWeights(bestship[n%nseeds],stray = 1*gencoef, colour = (100,240,240))
        elif(n < 90): 
            shp.newSpawn(colour = (100,100,240))
        elif(n < 1000): 
            shp.copyWeightsExper(bestship[n%nseeds],stray = 1*gencoef, colour = (240,100,240))
        n+=1
        shp.reset()

def moveAndDrawShips(screen, ships,maze):
    """ Calculate the new position that the ships will be at and draw them there. """
    allcrashed = True
    for shp in ships:
        if(shp.crashed == False):
            shp.moveShip(screen)
            if(maze.checkCollisions([shp.x,shp.y]) or shp.checkFuel() < 0):
                shp.crash()
            if(allcrashed): # The first one we find not crashed
                #shp.drawMatrix(screen)
                #shp.highlight(screen)
                allcrashed = False
        shp.drawShip(screen,maze)
    return allcrashed


############################################################
########## MAIN PROGRAM ####################################
############################################################

def playGame(width = 1600, height = 900, FPS = 40, basename = "BestShips",
             nships = 100, nseeds = 9, maxGen = 1000):
    
    # Initialization    
    size = width, height
    generation = 0
    frame = 0
    newBest = allcrashed = False
    
    time = pygame.time.Clock()
    mymaze = maze(height = height, width = width)
    walls = mymaze.obstacles
    checkpoints = mymaze.checkpoints
    checkpointPerLap = len(checkpoints)
    screen = pygame.display.set_mode(size)
    newbestsurface = [None]*nseeds
    
    ships = [ship(walls = walls,checkpoints = checkpoints) for i in range(nships)]
    bestship = []
    leadship = []
    
    # Main Loop
    while generation < maxGen:
        frame +=1
        # Check for quit
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
        mymaze.drawMap(screen)
    
        # Once everyone has crashed / run out of fuel we restart at the next generation
        if(allcrashed):
            generation +=1
            # Determine best ships
            bestship = getBestShip(ships,nseeds)
            # Flag to start displaying leaderboard
            newBest = True
            # Save top of each generation
            bestship[0].saveWeights(basename, generation)
            print("All crashed for generation " + str(generation) +"  Top Ship score: " + str(bestship[0].score) + "  at  " + str(bestship[0].weights[0][0][0]))
            # Create next generation
            copyShips(ships,bestship,nseeds,generation)
        # Move
        allcrashed = moveAndDrawShips(screen, ships,mymaze)
    
        # Draw all the overlay stuff
        drawHUD(screen,bestship,leadship,ships,nseeds,generation,newBest,frame,checkpoints)
 
        # Wait for next frame time          
        time.tick(FPS)
        # Updates screen
        pygame.display.flip()

playGame()