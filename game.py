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
    
def copyShips(ships,bestship,nseeds,generation,nships):
    """ Do the inter-generation copying of the best ships from the previous gen """
    gencoef = 1/(generation +1) 
    n = 0
    for shp in ships:
        if(n/nships < 0.2): 
            shp.copyWeights(bestship[n%nseeds],stray = 0.1*gencoef*gencoef, colour = (240,100,100))
        elif(n/nships < 0.4): 
            shp.copyWeights(bestship[n%nseeds],stray = 0.1*gencoef, colour = (240,240,100))
        elif(n/nships < 0.6): 
            shp.copyWeights(bestship[n%nseeds],stray = 0.5*gencoef, colour = (100,240,100))
        elif(n/nships < 0.8): 
            shp.copyWeights(bestship[n%nseeds],stray = 1*gencoef, colour = (100,200,240))
        #elif(n < 90): 
        #    shp.newSpawn(colour = (100,100,240))
        else: 
            shp.copyWeightsExper(bestship[n%nseeds],stray = 1*gencoef, colour = (240,100,240))
        n+=1
        shp.reset()

def moveShips(screen, ships,maze):
    """ Calculate the new position that the ships will be at """
    allcrashed = True
    for shp in ships:
        if(shp.crashed == False):
            shp.moveShip(screen,maze)
            if(maze.checkCollisions(shp.pos) or shp.checkFuel() < 0):
                shp.crash()
            if(allcrashed): # The first one we find not crashed
                allcrashed = False
    return allcrashed


def getLeadShips(ships):
    leadship = [max(ships, key = lambda x : x.getScore()*(1-int(x.crashed)))]
    return leadship

def drawShips(screen,ships,maze,midpos = None,followLead = False):
    if midpos is None or followLead is False: 
        midpos = (800,450)
    for shp in ships:
       shp.drawShip(screen,maze,midpos = midpos) 

def quitGame():
    """ Uninitialize everything and close pygame screen """
    pygame.display.quit()
    sys.exit()

def updateCameraPos(oldPos,target):
    MAXSPEED = 5
    temp = (target[0]-oldPos[0],target[1]-oldPos[1])
    tempsize = getDist(temp,(0,0))
    if(np.abs(tempsize) < MAXSPEED): 
        pos = target
    else: 
        pos = [oldPos[0]+temp[0]*MAXSPEED/tempsize,oldPos[1]+temp[1]*MAXSPEED/tempsize]
        
    return pos
def resetCameraPos(followLead):
    if followLead:
        return (50,50)
    else:
        return (800,450)

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
             saveFrames = True,victoryLap = False,followLead = False,displayHUD = True,
             displayOnScreen = True):
    print("#### STARTING GAME ####")
    print(basename)
    # Initialization    
    generation = 0
    frame = 0
    allcrashed = False
    bestship = None
    clock = pygame.time.Clock()
    mymaze = maze(height = height, width = width)
    ships = [ship(maze = mymaze, intermediates = intermediates, 
                  inputdistance = inputdistance, inputangle = inputangle) for i in range(nships)]
    leadships = None
    if(victoryLap):
        for i, shp in enumerate(ships):
            shp.loadWeights(basename,i,colour = (int(240*i/nships),int(240*(nships-i)/nships),20))
            shp.name = "Gen: "+str(i)
    if (displayHUD): headsUp = hud(maze = mymaze,victoryLap = victoryLap)
    
    camerapos = resetCameraPos(followLead)
    
    # Create pygame screen if we need to
    if(screen == None):
        size = width, height
        screen = pygame.display.set_mode(size)
    else:
        width = screen.get_width()
        height = screen.get_height()
    
    # Main Loop
    while generation < maxGen:
        #t1 = time.time()
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
            if(not victoryLap): saveBestships(bestship,basename,generation)
            # Create next generation
            copyShips(ships,bestship,nseeds,generation,nships)
            # Move camera to start location
            camerapos = resetCameraPos(followLead)
            generation +=1
        #t2 = time.time()    
        # Move the ships, returns true if every ship has crashed
        allcrashed = moveShips(screen,ships,mymaze)
        ## Update any moving parts to the maze
        mymaze.updateMap()
        # Find current leading ships
        if(displayOnScreen or followLead): leadships = getLeadShips(ships)
        if(followLead):
            camerapos = updateCameraPos(camerapos,leadships[0].pos)
        
        # Draw and update the map
        if(displayOnScreen): mymaze.drawMap(screen,midpos = camerapos,followLead = followLead)
        # Draw the ships
        if(displayOnScreen): drawShips(screen,ships,mymaze,midpos = camerapos,followLead = followLead)
        # Draw all the overlay stuff
        if displayHUD: headsUp.update(screen,generation,frame, bestships = bestship,ships = ships,
                       leadships = leadships,followLead = followLead,camerapos = camerapos)
        #t3 = time.time()
        # Save the image on screen if that's what we're doing
        if(saveFrames): saveFrame(screen,basename,frame)
        #t4 = time.time()
        # Wait for next frame time          
        if(displayOnScreen): clock.tick(FPS)
        #t5 = time.time()
        #print(str(t2-t1) + "  " +str(t3-t1) + "  " +str(t4-t1) + "  "+ str(t5-t1))
        # Updates screen
        if(displayOnScreen): pygame.display.flip()
    
    # END OF GAME
    return bestship

