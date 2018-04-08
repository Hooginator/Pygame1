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

    
def drawMap(screen, walls, checkpoints):
    """ Draw the background, walls and checkpoints."""
    screen.fill((0,0,0))
    drawWalls(walls,screen)
    #drawWalls(checkpoints,screen)

def drawHUD(screen,bestship,leadship,ships,nseeds,generation,newBest,frame,checkpoints):
    """ General function that will call all the smaller HUD pieces """
    if(newBest): drawLeaderboard(screen,bestship,nseeds,[0,150])
    #drawCurrentLeaders(screen,ships,nseeds,[0,150])
    leadship = max(ships, key = lambda x : x.getScore(checkpoints)*(1-int(x.crashed)))
    leadship.drawMatrix(screen,[50,750])
    leadship.highlight(screen)
        
    textsurface = myfont.render("Gen: "+str(generation), False, (240, 240, 240))
    screen.blit(textsurface,(0,0))  
def drawCurrentLeaders(screen,ships,nseeds,pos):
    """ Creates a list of who currently hjas the best score and displays that list. """
    currentLeaders = getBestShip(ships,10)
    drawLeaderboard(screen,currentLeaders,10,pos)
def drawLeaderboard(screen,bestship,nseeds,pos):
    """ Displays a list of the top scoring ships in bestship """
    for i in range(min(nseeds,10)):
        newbestsurface = myfont.render(str(i) + ":   " + str(int(bestship[i].score)) +"   "+bestship[i].getName(),  False, bestship[i].colour)
        screen.blit(newbestsurface,(pos[0],pos[1] + 50*i))
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

def moveAndDrawShips(ships,screen,walls,width,height):
    """ Calculate the new position that the ships will be at and draw them there. """
    allcrashed = True
    for shp in ships:
        if(shp.crashed == False):
            shp.moveShip(checkpoints)
            if(checkCollisions(walls,[shp.x,shp.y],width,height) or shp.checkFuel(len(checkpoints)) < 0):
                shp.crash(checkpoints)
            if(allcrashed): # The first one we find not crashed
                #shp.drawMatrix(screen)
                #shp.highlight(screen)
                allcrashed = False
        shp.drawShip(screen,walls,width,height)
    return allcrashed



############################################################
########## CONSTANTS #######################################
############################################################


# Screen constants
size = width, height = 1600, 900
FPS = 40
frame = 0

# Initialization     
time = pygame.time.Clock()
generation = 0
nseeds = 10

filename = "./data/BestShips"
fileext = ".txt"

ships = [ship(50,50,0,(240,100,100)) for i in range(100)]
bestship = []
leadship = []
walls = wall.maze(1)
checkpoints = wall.checkpoints(1)
checkpointPerLap = len(checkpoints)
screen = pygame.display.set_mode(size)
newbestsurface = [None]*nseeds
newBest = False
allcrashed = False



############################################################
########## MAIN PROGRAM ####################################
############################################################


while 1:
    frame +=1
    # Check for quit
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()
    drawMap(screen, walls, checkpoints)
    
    # Once everyone has crashed / run out of fuel we restart at the next generation
    if(allcrashed):
        generation +=1
        # Determine best ships
        bestship = getBestShip(ships,nseeds)
        # Flag to start displaying leaderboard
        newBest = True
        # Save top of each generation
        bestship[0].saveWeights(filename, generation)
        print("All crashed for generation " + str(generation) +"  Top Ship score: " + str(bestship[0].score) + "  at  " + str(bestship[0].weights[0][0][0]))
        # Create next generation
        copyShips(ships,bestship,nseeds,generation)
    # Move
    allcrashed = moveAndDrawShips(ships,screen,walls,width,height)
    
    # Draw all the overlay stuff
    drawHUD(screen,bestship,leadship,ships,nseeds,generation,newBest,frame,checkpoints)
 
    # Wait for next frame time          
    time.tick(FPS)
    # Updates screen
    pygame.display.flip()
