# -*- coding: utf-8 -*-
"""
Created on Mon Sep 26 13:28:32 2022

@author: frederik
"""

import math
import numpy as np
    
def animationData(nodes):
    """Creates dataset to be used"""
    
    #Arrays to contain x and y data   
    Xdata = []
    Ydata = []
    roles = []
    #Extract x and y data from each node and insert in arrays
    for x in range(len(nodes[0].PositionsX)):
        for i in nodes:
            Xdata.append(i.PositionsX[x])
            Ydata.append(i.PositionsY[x])
            roles.append(i.role[x])
            
    #Combine x and y data, transpose and return
    temp = np.array([Xdata, Ydata])
    AnimationData = np.transpose(temp)
    return AnimationData, roles

def checkInput(text):
    """Checks if input is a number"""
    while True:    
        num = input(text)
        try:
            value = int(num)
            return value
        except ValueError:
            try:
                value = float(num)
                print("Input is a float number and will be rounded down to closest integer")
                integerValue = math.floor(value)
                return integerValue
            except ValueError:
                print("This is not a number please enter a number")
        