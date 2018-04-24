# -*- coding: utf-8 -*-
"""
Created on Wed Jan 24 15:08:54 2018

@author: hoog

"""
# Imports the other classes and abse functions
from functions import *
from ship import *
from wall import *
from hud import *

############################################################
########## FUNCTIONS #######################################
############################################################

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
            shp.setName("Gggg")
        elif(n < 40): 
            shp.copyWeights(bestship[n%nseeds],stray = 0.1*gencoef, colour = (240,240,100))
            shp.setName("Gggg")
        elif(n < 60): 
            shp.copyWeights(bestship[n%nseeds],stray = 0.5*gencoef, colour = (100,240,100))
            shp.setName("Gggg")
        elif(n < 80): 
            shp.copyWeights(bestship[n%nseeds],stray = 1*gencoef, colour = (100,200,240))
            shp.setName("Gggg")
        #elif(n < 90): 
        #    shp.newSpawn(colour = (100,100,240))
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
            if(maze.checkCollisions(shp.pos) or shp.checkFuel() < 0):
                shp.crash()
            if(allcrashed): # The first one we find not crashed
                allcrashed = False
        shp.drawShip(screen,maze)
    return allcrashed

def quitGame():
    pygame.display.quit()
    sys.exit()


############################################################
########## MAIN PROGRAM ####################################
############################################################

def playGame(screen = None, width = 1600, height = 900, FPS = 40, basename = "BestShips",
             nships = 100, nseeds = 10, maxGen = 1000, intermediates = (8,),
             inputdistance = [50,100,150], inputangle = [1.2,0.6,0,-0.6,-1.2]):
    
    # Initialization    
    generation = 0
    frame = 0
    newBest = allcrashed = False
    
    if(screen == None):
        size = width, height
        screen = pygame.display.set_mode(size)
    else:
        width = screen.get_width()
        height = screen.get_height()
    
    time = pygame.time.Clock()
    mymaze = maze(height = height, width = width)
    walls = mymaze.obstacles
    checkpoints = mymaze.checkpoints
    checkpointPerLap = len(checkpoints)
    newbestsurface = [None]*nseeds
    
    ships = [ship(maze = mymaze, intermediates = intermediates,
                  inputdistance = inputdistance, inputangle = inputangle) for i in range(nships)]
    bestship = None
    leadship = []
    
    headsUp = hud(maze = mymaze)
    
    # Main Loop
    while generation < maxGen:
        frame +=1
        # Check for quit
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
        mymaze.drawMap(screen)
    
        # Once everyone has crashed / run out of fuel we restart at the next generation
        if(allcrashed):
            # Determine best ships
            mymaze.newGeneration()
            bestship = getBestShip(ships,nseeds)
            # Flag to start displaying leaderboard
            newBest = True
            f = open("./data/"+basename+"/topscores","a")
            for bs in bestship:
                f.write(str(bs.getScore()) + " ")
            f.write("\n")
            f.close()
            # Save top of each generation
            bestship[0].saveWeights(basename, generation)
            print("All crashed for generation " + str(generation) +"  Top Ship score: " + str(bestship[0].score) + "  at  " + str(bestship[0].weights[0][0][0]))
            # Create next generation
            copyShips(ships,bestship,nseeds,generation)
            generation +=1
        # Move
        allcrashed = moveAndDrawShips(screen, ships,mymaze)
    
        # Draw all the overlay stuff
        #drawHUD(screen,bestship,leadship,ships,nseeds,generation,newBest,frame)
        headsUp.update(screen,generation,frame, bestships = bestship,ships = ships)
        # Wait for next frame time          
        time.tick(FPS)
        # Updates screen
        pygame.display.flip()

