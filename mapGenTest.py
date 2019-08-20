#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 30 21:04:43 2018

@author: hoog
"""
import random
import copy
import pdb # DEBUG

DEBUG = True

directions = {"N": [-1,0],"S": [1,0],"E": [0,1],"W": [0,-1]}
FILE_PREFIX = "Map"
LEVEL = 1
FILE_SUFFIX = "_Wall.txt" 

    
# OLD STUFF
def mapArrayFromStr(wallPos):
    """ Takes a string of 1 or 0 corresponding to where walls are with new
    lines separated by \n"""
    wallArray = []
    i = 0 # 'i' counts the current line of the file we are on
    for line in wallPos.split('\n'):
        if(len(line) !=0):
            wallArray.append([line[0]])
        j = 1 # 'j' counts the current character we are on in line 'i'
        while j < len(line):
            wallArray[i].append(line[j])
            j+=1
        i+=1
    return wallArray    
        
def mapStrFromFile(filename):
    """ Reads the file given as a string for further processing """
    with open(filename, 'r') as myfile:
        data = myfile.read()
    return data
    

# Functions for making generateMapStr easier

def goBack(list,grid,pos,num):
    """Pass by reference and change everything in here"""
    global directions
    #if DEBUG: print("GOING BACK START OF FUNCTION")
    #if DEBUG: pdb.set_trace()
    for i in range(num):
        #print("Going back ",i+1," of ",num," times.  current pos: ",pos)
        #print("GOING BACK STATS:::::",pos,grid[pos[0]][pos[1]],list)
        #print2DGrid(grid)
        deltapos = directions[list[-1]]
        #print("DELTAPOS::::",deltapos)
        pos[0] =  pos[0]-deltapos[0]
        pos[1] =  pos[1]-deltapos[1]
        grid[pos[0]][pos[1]] = None
        list.pop()
        #print("Went back ",i+1," of ",num," times.  current pos: ",pos)
        #print("GOING BACK STATS:::::",pos,grid[pos[0]][pos[1]],list)
        #print2DGrid(grid)


def write2DGrid(grid):
    myfile = open(FILE_PREFIX+str(LEVEL)+FILE_SUFFIX,"w")
    for g in grid:
        for j in g:
            if j is None:
                myfile.write(".")
            else:
                myfile.write(str(j))
        myfile.write("\n")
    
def print2DGrid(grid):
    print()
    for g in grid:
        for j in g:
            if j is None:
                print(".",end="")
            else:
                print(j,end="")
        print()
    print()

def generateMapStr(final_XMAX,final_YMAX,minWidth=3,wallWidth=1,start_location = [0,0],TOTAL_CHECKPOINTS=10,START_DIRECTION = "E"):
    """ Will build a map of size [XMAX,YMAX] with a path throughout a minimum 
    of minWidth wide. I don't really know how to do this yet. manual for now"""
    # Normalize inputs
    final_XMAX = (final_XMAX-1)//(minWidth+wallWidth)*(minWidth+wallWidth)+1
    final_YMAX = (final_YMAX-1)//(minWidth+wallWidth)*(minWidth+wallWidth)+1

    # final_grid is what we will return at the end of the day, 1 for wall 0 for empty and 2-9 a-z A-Z or something for checkpoints
    final_grid = [[0 for _ in range(final_YMAX)] for _ in range(final_XMAX)]
    
    # Reduced effective grid by a factor of (minWidth+wallWidth)for throwing a sort of path finding algorithm in 
    # and then generatiung the larger grid from that 
    XMAX,YMAX = final_XMAX//(minWidth+wallWidth),final_YMAX//(minWidth+wallWidth)
    AREA = XMAX*YMAX
    effective_grid = [[None for _ in range(YMAX)] for _ in range(XMAX)] # This guy we will start at some spot and fill as we go along
        # With directions [N]orth [S]outh [E]ast [W]est or None if the position has not been assigned yet.  
    
    # Decide acceptable threshold
    MAX_UNUSED = 5#min(XMAX,YMAX)
    MAX_ITERATION = 5000#AREA**1.5//5
    
    # some constants and initializations
    current_pos = [s for s in start_location]
    relative_path = []
    
    done = False # we will be "done" if our start and end meet up
    count = 0
    # MAIN LOOP
    while AREA-len(relative_path) > MAX_UNUSED or done == False:
        
        #print("lol2")  
        if done:# Here we are next to the start location but we got here too early.  goback a bunch
            # Go back a random number of times
            togoback = random.randint(2,int(len(relative_path)//8+2))
            goBack(relative_path,effective_grid,current_pos,togoback)
            done = False
            continue
        
        # Normal exit if we are right beside the start location (or at least try to exit)
        rel_pos = [p-d for p,d in zip(current_pos,start_location)]
        if abs(rel_pos[0]) + abs(rel_pos[1]) == 1 and count > 1:
            done = True
            if rel_pos[0] == 1: temp_letter = "N"
            if rel_pos[0] == -1: temp_letter = "S"
            if rel_pos[1] == -1: temp_letter = "E"
            if rel_pos[1] == 1: temp_letter = "W"
            relative_path.append(temp_letter)
            effective_grid[start_location[0]+rel_pos[0]][start_location[1]+rel_pos[1]] = temp_letter
            current_pos = [s for s in start_location]
            continue
        
        #print("lol3")  
        # Generate dictionary of options that are available this time by copying all options and removing any that are blocked
        temp_directions = copy.copy(directions)
        if(current_pos[0] == 0 or effective_grid[current_pos[0]+directions["N"][0]][current_pos[1]+directions["N"][1]] is not None): del temp_directions["N"]
        if(current_pos[0] == XMAX-1 or effective_grid[current_pos[0]+directions["S"][0]][current_pos[1]+directions["S"][1]] is not None): del temp_directions["S"]
        if(current_pos[1] == YMAX-1 or effective_grid[current_pos[0]+directions["E"][0]][current_pos[1]+directions["E"][1]] is not None): del temp_directions["E"]
        if(current_pos[1] == 0 or effective_grid[current_pos[0]+directions["W"][0]][current_pos[1]+directions["W"][1]] is not None): del temp_directions["W"]
        
        
        # No options, we have to go back
        if len(temp_directions) == 0: 
        
            # Go back a random number of times
            togoback = random.randint(2,int(len(relative_path))//8+2)
            goBack(relative_path,effective_grid,current_pos,togoback)
            
            continue # for i in range(1000)
         
        # Choose an option and apply it
        if len(relative_path) == 0:
            temp_dir = START_DIRECTION
        else:
            temp_dir = random.choice(list(temp_directions.keys()))
        relative_path.append(temp_dir)
        effective_grid[current_pos[0]][current_pos[1]] = temp_dir
        current_pos = [p+d for p,d in zip(current_pos,temp_directions[temp_dir])]
        # if(count %1000 == 0):
            # print("Count: ",count)
            # print2DGrid(effective_grid)
        
        
        #print("lol1")    
            
        # Emergency exit
        count +=1
        if count > MAX_ITERATION:
            #print("Iteration number too high, ABORT")
            return False
    
    print("DONE  final grid:::")
    print2DGrid(effective_grid)
    
    # Time to transfer to 1s and 0s:
    # Basic version of the grid, essentially a lined grid where we will break down the walls
    # Where our path from the previous part of the algorithm takes us.
    # can optimise!!
    for i in range(final_XMAX):
        for j in range(final_YMAX):
            if i==0 or j==0 or i%(minWidth+wallWidth)==0 or j%(minWidth+wallWidth)==0 :
                final_grid[i][j] = 1
    
    
    
    # Walk through the grid using the path we generated and knock down all the walls to create a closed track
    current_pos = [s*(minWidth+wallWidth)+wallWidth for s in start_location] # top left
    total_path_length = len(relative_path)
    for n,p in enumerate(relative_path):
        # SMASH WALLS
        
        deltapos = [s*(minWidth+wallWidth) for s in directions[p]]
        deltazero = [minWidth if s==0 else s*(minWidth+wallWidth) for s in directions[p]]
        for i in range(current_pos[0],current_pos[0]+deltazero[0],deltazero[0]//abs(deltazero[0])):
            for j in range(current_pos[1],current_pos[1]+deltazero[1],deltazero[1]//abs(deltazero[1])):
                final_grid[i][j] = 0
        
        current_pos = [c+d for c,d in zip(current_pos,deltapos)]
        
        
        
    current_pos = [s*(minWidth+wallWidth)+wallWidth for s in start_location] # top left    
    temp_last_time = 1E99
    for n,p in enumerate(relative_path):
        # Separate loop for checkpoints
        
        deltapos = [s*(minWidth+wallWidth) for s in directions[p]]
        deltazero = [minWidth if s==0 else s*(minWidth+wallWidth) for s in directions[p]]
        
        
        if (n*TOTAL_CHECKPOINTS)%total_path_length < temp_last_time:
            # We place a checkpoint
            #pdb.set_trace()
            print(current_pos,deltazero,len(final_grid),len(final_grid[0]))
            final_grid[current_pos[0]+deltazero[0]//2][current_pos[1]+deltazero[1]//2] = chr(65+(n*TOTAL_CHECKPOINTS)//total_path_length)
            pass
        current_pos = [c+d for c,d in zip(current_pos,deltapos)]
        
        temp_last_time = (n*TOTAL_CHECKPOINTS)%total_path_length
        
    print2DGrid(final_grid)
    
    #SAVE GRID
    write2DGrid(final_grid)
    
    
    return True

if __name__ == "__main__":
    count = 0
    # loop through until we get one (returns True)
    while True:
        count +=1 
        #print("lol")
        if(generateMapStr(40,40)):
            break
            #Emergency Exit
        if(count > 1000):
            print("BIG LOOP ABORT")
            break
        if(count %10 == 0):
            print(count," failed so far")
    print("Done  all the things")
    print(chr(65))