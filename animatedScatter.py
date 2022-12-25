# -*- coding: utf-8 -*-
"""
Created on Wed Oct 12 15:32:35 2022

@author: frederik
"""

from time import time
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import animation


class AnimatedScatter(object):
    
    def __init__(self, numNodes, size, frames, nodeCoordinates, nodeRoles, simulationSpeed):
        """Init function for the animation"""
        #Set up variables
        self.numNodes = numNodes
        self.scatterSize = size
        self.frameCount = frames
        self.nodeCoordinates = nodeCoordinates
        self.nodeRoles = np.array(nodeRoles)
        self.timeElapsed = 0
        self.frameInterval = (1/60)/simulationSpeed

        # Setup figure and axes and text
        self.fig, self.ax = plt.subplots()
        self.time_text = self.ax.text((self.scatterSize)/2 - 0.075*self.scatterSize, self.scatterSize - 0.05*self.scatterSize, "Time:")
       
        #Setup interval between frames 
        self.setup_plot()
        t0 = time()
        self.update(0)
        t1 = time()
        interval = 1000*self.frameInterval - (t1 - t0)
        
        # Setup FuncAnimation
        self.ani = animation.FuncAnimation(self.fig, self.update, frames = self.frameCount, interval = interval,
                                          init_func=self.setup_plot, blit=True, repeat=False)
        
        # self.ani.save('test.gif', writer = 'pillow')
        
    def setup_plot(self):
        """Initial drawing of the scatter plot."""
        x, y = np.c_[self.nodeCoordinates[:0,0], self.nodeCoordinates[:0,1]].T
        c = []
        
        self.scat = self.ax.scatter(x, y, c = c, edgecolor="black", cmap = 'jet', vmin = 0, vmax = 1)
        self.ax.axis([0, self.scatterSize, 0, self.scatterSize])
        
        return self.scat,

    def update(self, i):
        """Update the scatter plot."""
        data = self.nodeCoordinates[(i-1)*self.numNodes:i*self.numNodes]
        colors = self.nodeRoles[(i-1)*self.numNodes:i*self.numNodes]
        # Set x and y data
        self.scat.set_offsets(data[:, :2])
        self.scat.set_array(colors)
        #Update elapsed time and display if not first frame
        self.timeElapsed = i*0.01666
        if i > 0: 
            self.time_text.set_text('Time = %.1f' % self.timeElapsed)

        return self.scat, self.time_text,