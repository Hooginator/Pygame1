#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 30 21:04:43 2018

@author: hoog
"""
import random
import copy
import pdb # DEBUG
import time

DEBUG = True

DIRECTIONS = {"N": (-1,0),"S": (1,0),"E": (0,1),"W": (0,-1)}
OPPOSITE_DIRECTIONS = {"N":"S","S":"N","E":"W","W":"E"}
REVERSE_DIRECTIONS = {(-1,0):"N",(1,0):"S",(0,1):"E",(0,-1):"W"}
FILE_PREFIX = "Map"
FILE_SUFFIX = "_Wall.txt" 
LEVEL = 2

    
# # OLD STUFF
# def mapArrayFromStr(wallPos):
    # """ Takes a string of 1 or 0 corresponding to where walls are with new
    # lines separated by \n"""
    # wallArray = []
    # i = 0 # 'i' counts the current line of the file we are on
    # for line in wallPos.split('\n'):
        # if(len(line) !=0):
            # wallArray.append([line[0]])
        # j = 1 # 'j' counts the current character we are on in line 'i'
        # while j < len(line):
            # wallArray[i].append(line[j])
            # j+=1
        # i+=1
    # return wallArray    
        
# def mapStrFromFile(filename):
    # """ Reads the file given as a string for further processing """
    # with open(filename, 'r') as myfile:
        # data = myfile.read()
    # return data
    

# Functions for making generateMapStr easier

class MapGenerator(object):
    def __init__(self, X_in, Y_in, minWidth=3, wallWidth=1,start_location = (0,0),start_direction = "E",total_checkpoints=10):
    
        # Final sizes trimmed a bit to fit the path and wall widths  
        self.final_XMAX = (X_in-1)//(minWidth+wallWidth)*(minWidth+wallWidth)+1
        self.final_YMAX = (Y_in-1)//(minWidth+wallWidth)*(minWidth+wallWidth)+1
        
        # Reduced sizes for path finding algorithm
        self.XMAX,self.YMAX = self.final_XMAX//(minWidth+wallWidth),self.final_YMAX//(minWidth+wallWidth)
        self.area = self.XMAX*self.YMAX
        
        # Generic variables to save
        self.minWidth = minWidth
        self.wallWidth = wallWidth
        self.start_location = start_location
        self.start_direction = start_direction
        self.total_checkpoints = total_checkpoints
        
        
        self.reset()
        
    def reset(self):
        # Initialize final grid of zeros to be printed
        self.final_grid = [[0 for _ in range(self.final_YMAX)] for _ in range(self.final_XMAX)]
        
        # Reduced effective grid by a factor of (minWidth+wallWidth) to normalize for path finding.  Final results will be higher resolution versions of this
        self.effective_grid = [[None for _ in range(self.YMAX)] for _ in range(self.XMAX)]  
        
        # List version of the paths in effective_grid
        self.relative_path = []
        self.from_end_path = []
        
    
    def getDirectionOptions(self,pos,grid):
        temp_directions = copy.copy(DIRECTIONS)
        # Remove any directions that lead off map
        if(pos[0] == 0): del temp_directions["N"]
        if(pos[0] == self.XMAX-1): del temp_directions["S"]
        if(pos[1] == self.YMAX-1): del temp_directions["E"]
        if(pos[1] == 0):  del temp_directions["W"]
        
        # Remove options that lead onto used spot
        for d in DIRECTIONS:
            if d in temp_directions and grid[pos[0] + DIRECTIONS[d][0]][pos[1] + DIRECTIONS[d][1]] is not None: del temp_directions[d]
            
        return temp_directions
        
    
    def getFastestPath(self,start,end,max_length = 100): # need too thionk this one through a bit, I am just thinking around in circles now
            # Create temporary grid that I will fill in with previously explored tilesfor path finding
            temp_grid = list(map(list, self.effective_grid)) 
            # frontline will be a dict of positions that I have to check as keys with values of the path they took so far
            frontline = {tuple(start):[]}
            for l in range(max_length):
                next_frontline = {}
                #print2DGrid(temp_grid)
                for f in frontline:
                    # If we arer 1 away we are done
                    if abs(f[0] - end[0]) + abs(f[1] - end[1]) == 1:
                        return frontline[f] + [f] 
                
                    temp_grid[f[0]][f[1]] = "o"
                    for d in self.getDirectionOptions(f,temp_grid):
                        if temp_grid[f[0]+DIRECTIONS[d][0]][f[1]+DIRECTIONS[d][1]] is None:
                            next_frontline[(f[0]+DIRECTIONS[d][0],f[1]+DIRECTIONS[d][1])] = frontline[f] + [f]
                        
                frontline = next_frontline  
            print("NO PATH")
            return None
                    
                    
    def generatePath(self,max_unused = None,max_iterations = 10000):
        
        def canEndCheck():
            """ Checks if we are close enough to end with few enough unused spaces """
            rel_pos = tuple([p-d for p,d in zip(current_pos,end_pos)])
            print(abs(rel_pos[0]) , abs(rel_pos[1]),self.area-len(self.relative_path) - len(self.from_end_path),max_unused)
            return abs(rel_pos[0]) + abs(rel_pos[1]) == 1 and count > 1 and self.area-len(self.relative_path) - len(self.from_end_path) < max_unused
        
        
        
        if max_unused ==  None:
            max_unused = self.area / 1.2
        
        # some constants and initializations
        current_pos = [s for s in self.start_location]
        end_pos = [s for s in self.start_location]
        
        # Loop variables
        done = False # Signifies when the loop is closed, it might have done = True but not be long enough and return to building
        count = 0
        count_since_last_reset = 0
        
        # do first step(s)
        for _ in range(3):
            self.effective_grid[current_pos[0]][current_pos[1]] = self.start_direction
            current_pos = [c+d for c,d in zip(current_pos,DIRECTIONS[self.start_direction])]
            self.relative_path.append(self.start_direction)
        
        # MAIN LOOP
        while done == False:
            count +=1
            count_since_last_reset +=1
            # Check if we are able to close the loop
            if canEndCheck():
                # Option to close the loop here
                
                temp_dir = REVERSE_DIRECTIONS[(end_pos[0]-current_pos[0],end_pos[1]-current_pos[1])]
                
                self.relative_path.append(temp_dir)
                self.effective_grid[current_pos[0]][current_pos[1]] = temp_dir
                
                done = True
                continue
            
            temp_directions = self.getDirectionOptions(current_pos,self.effective_grid)

                
                
            # If no options remain, we have hit a dead end and must go back some steps and restart loop
            if len(temp_directions) == 0: 
                # Go back a random number of times
                togoback = random.randint(2,int(len(self.relative_path))//(2*count_since_last_reset)+2)
                goBack(self.relative_path,self.effective_grid,current_pos,togoback)
                count_since_last_reset /= 10
                continue 
         
            # Choose a direction option and apply it

            temp_dir = random.choice(list(temp_directions.keys()))
            self.relative_path.append(temp_dir)
            self.effective_grid[current_pos[0]][current_pos[1]] = temp_dir
            current_pos = [p+d for p,d in zip(current_pos,temp_directions[temp_dir])]
            
            if count %10 == 0:
                print2DGrid(self.effective_grid)
                # Impossible to end, gotta cut some
                while self.getFastestPath(current_pos,end_pos) == None:
                    count_since_last_reset +=1
                    print2DGrid(self.effective_grid)
                    togoback = random.randint(2,int(len(self.relative_path))//(count_since_last_reset**0.5)+2)
                    goBack(self.relative_path,self.effective_grid,current_pos,togoback)
                    count_since_last_reset /= 10
                time.sleep(0.3)

       
        print2DGrid(self.effective_grid)
        
        
    def write_true_grid(self):
         # Time to transfer to 1s and 0s:
        # Basic version of the grid, essentially a lined grid where we will break down the walls
        # Where our path from the previous part of the algorithm takes us.
        # can optimise!!
        
        
        # Instead lets just build the track from 0s as we go,
        
        def build_walls(dir,pos,prev):
            # actually add the 1s to final grid
            todraw = ["N","S","W","E"]
            todraw.remove(OPPOSITE_DIRECTIONS[prev])
            todraw.remove(dir)
            print(todraw)
            for d in todraw:
                for i in range(self.minWidth + self.wallWidth*2):
                    #lself.final_grid[][]
                    #print(pos,i)
                    if d == "W":
                        self.final_grid[pos[0] +i][pos[1]] = 1
                    if d == "E":
                        self.final_grid[pos[0]+i][pos[1] + self.minWidth+ self.wallWidth] = 1
                    if d == "N":
                        self.final_grid[pos[0] ][pos[1] +i] = 1
                    if d == "S":
                        self.final_grid[pos[0] +self.minWidth + self.wallWidth][pos[1]  + i] = 1 
            print2DGrid(self.final_grid)
            input()
        
        current_pos = [s for s in self.start_location] # top left
        total_path_length = len(self.relative_path)
        for n,p in enumerate(self.relative_path):
            if n==0:
                last_direction = self.relative_path[-1]
            build_walls(p,current_pos,last_direction)    
            deltapos = [s*(self.minWidth+self.wallWidth) for s in DIRECTIONS[p]]
            #deltazero = [self.minWidth if s==0 else s*(self.minWidth+self.wallWidth) for s in DIRECTIONS[p]]
            #for i in range(current_pos[0],current_pos[0]+deltazero[0],deltazero[0]//abs(deltazero[0])):
            #    for j in range(current_pos[1],current_pos[1]+deltazero[1],deltazero[1]//abs(deltazero[1])):
            #        self.final_grid[i][j] = 0
            current_pos = [c+d for c,d in zip(current_pos,deltapos)]
            
            last_direction = p
            
            
            
            
        # Old smashy way
        # for i in range(self.final_XMAX):
            # for j in range(self.final_YMAX):
                # if i==0 or j==0 or i%(self.minWidth+self.wallWidth)==0 or j%(self.minWidth+self.wallWidth)==0 :
                    # self.final_grid[i][j] = 1
        
        # # SMASH WALLS
        # # Walk through the grid using the path we generated and knock down all the walls to create a closed track
        # current_pos = [s*(self.minWidth+self.wallWidth)+self.wallWidth for s in self.start_location] # top left
        # total_path_length = len(self.relative_path)
        # for n,p in enumerate(self.relative_path):
            # deltapos = [s*(self.minWidth+self.wallWidth) for s in DIRECTIONS[p]]
            # deltazero = [self.minWidth if s==0 else s*(self.minWidth+self.wallWidth) for s in DIRECTIONS[p]]
            # for i in range(current_pos[0],current_pos[0]+deltazero[0],deltazero[0]//abs(deltazero[0])):
                # for j in range(current_pos[1],current_pos[1]+deltazero[1],deltazero[1]//abs(deltazero[1])):
                    # self.final_grid[i][j] = 0
            # current_pos = [c+d for c,d in zip(current_pos,deltapos)]  
            
            
        # CHECKPOINTS 
        # Steps through the grid and every so often drops a checkpoint equally spaced   
        current_pos = [s*(self.minWidth+self.wallWidth)+self.wallWidth for s in self.start_location] # top left    
        temp_last_time = 1E99
        for n,p in enumerate(self.relative_path):
            deltapos = [s*(self.minWidth+self.wallWidth) for s in DIRECTIONS[p]]
            deltazero = [self.minWidth if s==0 else s*(self.minWidth+self.wallWidth) for s in DIRECTIONS[p]]
            if (n*self.total_checkpoints)%total_path_length < temp_last_time:
                # We place a checkpoint
                print(current_pos,deltazero,len(self.final_grid),len(self.final_grid[0]))
                self.final_grid[current_pos[0]+deltazero[0]//2][current_pos[1]+deltazero[1]//2] = chr(65+(n*self.total_checkpoints)//total_path_length)
                pass
            current_pos = [c+d for c,d in zip(current_pos,deltapos)]
            temp_last_time = (n*self.total_checkpoints)%total_path_length   
        print2DGrid(self.final_grid)
        
        # TRIM
        # From the edges, see if any of the walls are unneeded for the actual race.  each wall takes more space and I think it would just look better without the clutter.
        
        void_cells = {}
        for edge in getEdges(self.effective_grid):
            if edge == ".":
                pass
        
        
        #SAVE GRID
        write2DGrid(self.final_grid,FILE_PREFIX+str(LEVEL)+FILE_SUFFIX)
    
    
    
    
        
        
        
def getEdges(grid):
    """ Returns a list of all coordinates along the edges of a grid, order is irrelevant"""
    X = len(grid)
    Y = len(grid[0])
    mylist = []
    for i in range(X):
        mylist.append([i,0])
        mylist.append([i,Y-1])
    
    for j in range(Y):
        mylist.append([0,j])
        mylist.append([X-1,j])
    return(mylist)

def goBack(list,grid,pos,num):
    """Our path is going back [num] steps.  For each step back we
    change the current position [pos] appropriately, change that spot
    in our reduced [grid] back to None and pop the last direction off of [list]
    """
    for i in range(num):
        deltapos = DIRECTIONS[list[-1]]
        pos[0] =  pos[0]-deltapos[0]
        pos[1] =  pos[1]-deltapos[1]
        grid[pos[0]][pos[1]] = None
        list.pop()


def write2DGrid(grid,filename):
    """ Writes given 2D [grid] to the [filename] specified """
    myfile = open(filename,"w")
    for g in grid:
        for j in g:
            if j is None:
                myfile.write(".")
            else:
                myfile.write(str(j))
        myfile.write("\n")
    
def print2DGrid(grid):
    """Prints out our beautiful 2D [grid] of characters provided """
    print()
    for g in grid:
        for j in g:
            if j is None:
                print(".",end="")
            else:
                print(j,end="")
        print()
    print()

def generateMapStr(XMAX_in,YMAX_in,minWidth=3,wallWidth=1,start_location = [0,0],TOTAL_CHECKPOINTS=10,START_DIRECTION = "E",LEVEL = 2):
    """ Will build a map of size [XMAX,YMAX] with a path throughout a minimum 
    of minWidth wide.  Builds a path by traversing the XMAX by YMAX space 
    if the path hits a dead end it is sent back a few tiles, if the path connects
    back to the start it will end the loop successfuly and save teh map
    """
        
    # Normalize inputs.  I take the required full grid size and make it a proper 
    # multiple of the width of the passage and walls.  
    final_XMAX = (XMAX_in-1)//(minWidth+wallWidth)*(minWidth+wallWidth)+1
    final_YMAX = (YMAX_in-1)//(minWidth+wallWidth)*(minWidth+wallWidth)+1

    # final_grid is what we will return at the end of the day, 1 for wall 
    # 0 for empty and 2-9 a-z A-Z or something for checkpoints
    final_grid = [[0 for _ in range(final_YMAX)] for _ in range(final_XMAX)]
    
    # Reduced effective grid by a factor of (minWidth+wallWidth)for throwing a sort of path finding algorithm in 
    # and then generatiung the larger grid from that 
    XMAX,YMAX = final_XMAX//(minWidth+wallWidth),final_YMAX//(minWidth+wallWidth)
    AREA = XMAX*YMAX
    
    # Will fill with directions [N]orth [S]outh [E]ast [W]est or None if the position has not been assigned yet.  
    effective_grid = [[None for _ in range(YMAX)] for _ in range(XMAX)]  
    
    # List version of the paths in effective_grid
    relative_path = []
    from_end_path = []
    
    # Decide acceptable threshold
    MAX_UNUSED = 8*XMAX#Maximum numbver of "dead" spots in the effective grid
    MAX_ITERATION = 50000# Maximum number of times we will try to make a maze
    
    # some constants and initializations
    current_pos = [s for s in start_location]
    end_pos = [s for s in start_location]
    
    # Loop variables
    done = False # Signifies when the loop is closed, it might have done = True but not be long enough and return to building
    count = 0
    
    # MAIN LOOP
    while done == False:
        
        if done:
            # Here we are next to the start location but we got here too early
            # Go back a random number of times
            togoback = random.randint(int(len(relative_path)/3+2),int(len(relative_path)/1.1+2)) # probably needs tuning
            goBack(relative_path,effective_grid,current_pos,togoback) # Go back specified number of steps
            done = False
            continue
        
        # Normal attempt to exit if we are right beside the start location 
        # Add in last path step to complete the circuit, then continue loop 
        # to check if we have used enough spaces
        rel_pos = tuple([p-d for p,d in zip(current_pos,end_pos)])
        if abs(rel_pos[0]) + abs(rel_pos[1]) == 1 and count > 1 and AREA-len(relative_path) < MAX_UNUSED:
            done = True
            print("attempting to end")
            temp_letter = REVERSE_DIRECTIONS[rel_pos]
            relative_path.append(temp_letter)
            effective_grid[start_location[0]+rel_pos[0]][start_location[1]+rel_pos[1]] = temp_letter
            current_pos = [s for s in end_pos]
            continue
        
        # Generate dictionary of direction options that are available this time by copying 
        # all options and removing any that are blocked by our previous path or boundaries
        temp_directions = copy.copy(directions)
        if(current_pos[0] == 0 or effective_grid[current_pos[0]+directions["N"][0]][current_pos[1]+directions["N"][1]] is not None): del temp_directions["N"]
        if(current_pos[0] == XMAX-1 or effective_grid[current_pos[0]+directions["S"][0]][current_pos[1]+directions["S"][1]] is not None): del temp_directions["S"]
        if(current_pos[1] == YMAX-1 or effective_grid[current_pos[0]+directions["E"][0]][current_pos[1]+directions["E"][1]] is not None): del temp_directions["E"]
        if(current_pos[1] == 0 or effective_grid[current_pos[0]+directions["W"][0]][current_pos[1]+directions["W"][1]] is not None): del temp_directions["W"]
        
        
        # If no options remain, we have hit a dead end and must go back some steps and restart loop
        if len(temp_directions) == 0: 
            # Go back a random number of times
            togoback = random.randint(int(len(relative_path)/8)+2,int(len(relative_path)/2)+2)
            goBack(relative_path,effective_grid,current_pos,togoback)
            continue # for i in range(1000)
         
        # Choose a direction option and apply it
        if len(relative_path) == 0:
            temp_dir = START_DIRECTION
        else:
            temp_dir = random.choice(list(temp_directions.keys()))
        relative_path.append(temp_dir)
        effective_grid[current_pos[0]][current_pos[1]] = temp_dir
        current_pos = [p+d for p,d in zip(current_pos,temp_directions[temp_dir])]

        # Emergency exit, for if we are trying too long on one attempt
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
    
    
    
    
    # SMASH WALLS
    # Walk through the grid using the path we generated and knock down all the walls to create a closed track
    current_pos = [s*(minWidth+wallWidth)+wallWidth for s in start_location] # top left
    total_path_length = len(relative_path)
    for n,p in enumerate(relative_path):
        deltapos = [s*(minWidth+wallWidth) for s in directions[p]]
        deltazero = [minWidth if s==0 else s*(minWidth+wallWidth) for s in directions[p]]
        for i in range(current_pos[0],current_pos[0]+deltazero[0],deltazero[0]//abs(deltazero[0])):
            for j in range(current_pos[1],current_pos[1]+deltazero[1],deltazero[1]//abs(deltazero[1])):
                final_grid[i][j] = 0
        current_pos = [c+d for c,d in zip(current_pos,deltapos)]  
        
        
    # CHECKPOINTS 
    # Steps through the grid and every so often drops a checkpoint equally spaced   
    current_pos = [s*(minWidth+wallWidth)+wallWidth for s in start_location] # top left    
    temp_last_time = 1E99
    for n,p in enumerate(relative_path):
        deltapos = [s*(minWidth+wallWidth) for s in directions[p]]
        deltazero = [minWidth if s==0 else s*(minWidth+wallWidth) for s in directions[p]]
        if (n*TOTAL_CHECKPOINTS)%total_path_length < temp_last_time:
            # We place a checkpoint
            print(current_pos,deltazero,len(final_grid),len(final_grid[0]))
            final_grid[current_pos[0]+deltazero[0]//2][current_pos[1]+deltazero[1]//2] = chr(65+(n*TOTAL_CHECKPOINTS)//total_path_length)
            pass
        current_pos = [c+d for c,d in zip(current_pos,deltapos)]
        temp_last_time = (n*TOTAL_CHECKPOINTS)%total_path_length   
    print2DGrid(final_grid)
    
    #SAVE GRID
    write2DGrid(FILE_PREFIX+str(LEVEL)+FILE_SUFFIX)
    
    
    return True

if __name__ == "__main__":
    temp = MapGenerator(50,50,)
    temp.generatePath()
    temp.write_true_grid()
    # count = 0
    # totalmapstomake = 10
    # for i in range(totalmapstomake):
        # while True:
            # count +=1 
            # if(generateMapStr(200,200,LEVEL=i)):
                # break
            # #Emergency Exit
            # if(count > 10000):
                # print("BIG LOOP ABORT")
                # break
            # if(count %10 == 0):
                # print(count," failed so far")
    # print("Done  all the things")
    # print(chr(65))