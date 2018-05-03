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
    """ Determine and return ships with the highest score """
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
            shp.copyWeights(bestship[n%nseeds],stray = 1*gencoef, colour = (100,200,240))
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
    """ Uninitialize everything and close pygame screen """
    pygame.display.quit()
    sys.exit()

def saveBestships(bestships,basename,gen):
    """ Save top weight of each generation and the top 10 scores"""
    bestships[0].saveWeights(basename, gen)
    if(gen == 0):
        f = open("./data/"+basename+"/topscores","w")
    else:
        f = open("./data/"+basename+"/topscores","a")
    for bs in bestships:
        f.write(str(bs.getScore()) + " ")
    f.write("\n")
    f.close()
    print("All crashed for generation " + str(gen) +"  Top Ship score: " 
          + str(bestships[0].score) + "  at  " + str(bestships[0].weights[0][0][0]))
            
def saveFrame(screen,basename,frame):
    """ Saves the currently displayed image on screen """
    if not os.path.exists("./data/"+basename+"/frames/"):
        os.makedirs("./data/"+basename+"/frames/")
    pygame.image.save(screen,"./data/"+basename+"/frames/frame"+str(frame).zfill(10))

############################################################
########## MAIN PROGRAM ####################################
############################################################

def playGame(screen = None, width = 1600, height = 900, FPS = 90, basename = "BestShips",
             nships = 100, nseeds = 10, maxGen = 1000, intermediates = (8,),
             inputdistance = [50,100,150], inputangle = [1.2,0.6,0,-0.6,-1.2],
             saveFrames = True,victoryLap = False):
    print("#### STARTING GAME ####")
    # Initialization    
    generation = 0
    frame = 0
    allcrashed = False
    bestship = None
    time = pygame.time.Clock()
    mymaze = maze(height = height, width = width)
    ships = [ship(maze = mymaze, intermediates = intermediates, 
                  inputdistance = inputdistance, inputangle = inputangle) for i in range(nships)]
    if(victoryLap):
        for i, shp in enumerate(ships):
            shp.loadWeights(basename,i)
            shp.name = "Gen: "+str(i)
    headsUp = hud(maze = mymaze,victoryLap = victoryLap)
    
    # Create pygame screen if we need to
    if(screen == None):
        size = width, height
        screen = pygame.display.set_mode(size)
    else:
        width = screen.get_width()
        height = screen.get_height()
    
    # Main Loop
    while generation < maxGen:
        frame +=1
        # Check for quit
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
    
        # Once everyone has crashed / run out of fuel we restart at the next generation
        if(allcrashed):
            # Reinitialize the environment
            mymaze.newGeneration()
            # Determine best ships
            bestship = getBestShip(ships,nseeds)
            # Save the best ships
            saveBestships(bestship,basename,generation)
            # Create next generation
            copyShips(ships,bestship,nseeds,generation)
            generation +=1
        # Draw and update the map
        mymaze.drawMap(screen)
        # Move and draw the ships, returns true is each ship has crashed
        allcrashed = moveAndDrawShips(screen, ships,mymaze)
        # Draw all the overlay stuff
        headsUp.update(screen,generation,frame, bestships = bestship,ships = ships)
        # Save the image on screen if that's what we're doing
        if(saveFrames): saveFrame(screen,basename,frame)
        # Wait for next frame time          
        time.tick(FPS)
        # Updates screen
        pygame.display.flip()
    
    # END OF GAME
    return bestship

