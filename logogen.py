#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec  8 14:50:29 2018

@author: hoog
"""

from functions import *


def getLogo():
    ofx,ofy = 4,2
    c2 = (0,0,255)
    c1 = (40,40,40)
    logo = pygame.Surface((400,200))
    m1 = myfont.render("MATRIX", True, c1)
    m2 = myfont.render("MATRIX", True, c2)
    r1 = myfont.render("RACER", True, c1)
    r2 = myfont.render("RACER", True, c2)
    lb1 = myfontbig.render("[",True,c1)
    lb2 = myfontbig.render("[",True,c2)
    rb1 = myfontbig.render("]",True,c1)
    rb2 = myfontbig.render("]",True,c2)
    logo.blit(m1,(30,25))
    logo.blit(r1,(45,70))
    logo.blit(lb1,(0,0))
    logo.blit(rb1,(160,0))
    logo.blit(m2,(30+ofx,25+ofy))
    logo.blit(r2,(45+ofx,70+ofy))
    logo.blit(lb2,(ofx,ofy))
    logo.blit(rb2,(160+ofx,ofy))
    return logo



myfont = pygame.font.SysFont("dejavuserif", 45, bold = False)
myfontbig = pygame.font.SysFont("dejavuserif", 150, bold = False)
clock = pygame.time.Clock()

screen = pygame.display.set_mode((900,600))

# render text
label = getLogo()
screen.fill((0,0,0))
screen.blit(label, (300, 200))
pygame.display.flip()
clock.tick(0.1)
pygame.display.quit()

