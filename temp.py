import numpy as np
x_bigger = 0
y_bigger = 0
for i in range(100000):
    x = np.random.random()*4
    y = np.random.random()*3
    if x > y:
        x_bigger +=1
    elif y > x: 
        y_bigger +=1
print("X Bigger Fraction: " + str(x_bigger/(x_bigger+y_bigger)))