Ship wall collision change: 
instead of pick a spot, is it in a wall, we draw the line out from the player, finding the ordered list of all squares that line would mathematically pass through
IF WE KEEP RIGID SQUARE ENDS (I don't really like that but I think it's worth) this should be easy, 
then check one at a time (maybe have a dict of already cheacked from other liens)
 and whenever you hit a first wall, calculate the distance along the line and use that float as input


NEED
1. map function: given IRL pos, an angle and a distance return list of cells (tuple of coordinates) 