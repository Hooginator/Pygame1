#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 14 13:30:41 2018

@author: hoog
"""

from game import *


for i in range(2):
    playGame(maxGen = 1, basename = "Tournament_"+str(i))
quitGame()