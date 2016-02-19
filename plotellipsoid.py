"""
Module for plotting ellipsoids.

Basic Usage:
    Generate EllipsoidImage object (using existing matplotlib figure axes if required)
    plotellipsoid(ellipsoidobject) will hten plot 3D ellipsoid with basic settings
    
"""

from __future__ import division
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt



class EllipsoidImage(object):
    def __init__(self, figure=None, axes=None):
        """ Initialise figure and axes for ellipsoid plot """
        if figure is None:
            self.fig = plt.figure()
        else:   
            self.fig = figure
        if axes is None:
            self.ax = self.fig.add_subplot(111, projection='3d')
        else:
            self.ax = axes
        
        # Attributes to hold plots
        self.ellipaxes = None
        self.ellipframe = None
        self.points = None

    def plotell(self, 
                ellipsoid, 
                plotpoints=True, 
                plotaxes=True, 
                cagecolor='b',
                axcols = None,
                cagealpha=0.2,                        
                pointcolor='r', 
                pointmarker='o',
                pointscale=100,
                title=None,
                equalaxes=True):
        """Plot an ellipsoid"""

        if axcols is None:
            axcols = [cagecolor]*3
        
        if ellipsoid.radii is None:
            raise ValueError("Ellipsoid radii are not present")
        elif ellipsoid.rotation is None:
            raise ValueError("Ellipsoid rotation is not present")
            
        u = np.linspace(0.0, 2.0 * np.pi, 100)
        v = np.linspace(0.0, np.pi, 100)
        
        # cartesian coordinates that correspond to the spherical angles:
        x = ellipsoid.radii[0] * np.outer(np.ones_like(u), np.cos(v))
        y = ellipsoid.radii[1] * np.outer(np.sin(u), np.sin(v))
        z = ellipsoid.radii[2] * np.outer(np.cos(u), np.sin(v))
        
        # rotate accordingly
        for i in range(len(x)):
            for j in range(len(x)):
                [x[i,j],y[i,j],z[i,j]] = np.dot([x[i,j],y[i,j],z[i,j]], ellipsoid.rotation) + ellipsoid.centre

        if plotaxes:
            # Generate ellipsoid axes
            axes = np.eye(3)*ellipsoid.radii
            # rotate accordingly
            axes = np.dot(axes, ellipsoid.rotation)
            # plot axes
            self.ellipaxes=[]
            for i, p in enumerate(axes):
                X3 = np.linspace(-p[0], p[0], 100) + ellipsoid.centre[0]
                Y3 = np.linspace(-p[1], p[1], 100) + ellipsoid.centre[1]
                Z3 = np.linspace(-p[2], p[2], 100) + ellipsoid.centre[2]
                self.ellipaxes.append(self.ax.plot(X3, Y3, Z3, color=axcols[i]))
                
        # plot ellipsoid
        self.ellipframe = self.ax.plot_wireframe(x, y, z,  rstride=4, cstride=4, color=cagecolor, alpha=cagealpha)
        
        if plotpoints:
            self.points = self.ax.scatter(ellipsoid.points[:,0], ellipsoid.points[:,1], ellipsoid.points[:,2], c=pointcolor, marker=pointmarker, s=pointscale)

        # Label plot
        if title is not None:
            self.ax.set_title(title)
        self.ax.set_xlabel('x')
        self.ax.set_ylabel('y')
        self.ax.set_zlabel('z')
        
        # Make axes lengths equal if needed (otherwise limits are taken from data
        if equalaxes:
            limits = [self.ax.get_xlim(), self.ax.get_ylim(), self.ax.get_zlim()]
            ranges = [abs(self.ax.get_xlim()[1] - self.ax.get_xlim()[0]), abs(self.ax.get_ylim()[1] - self.ax.get_ylim()[0]), abs(self.ax.get_zlim()[1] - self.ax.get_zlim()[0])]
            maxrange = np.argmax(ranges)
            self.ax.set_xlim(limits[maxrange])
            self.ax.set_ylim(limits[maxrange])
            self.ax.set_zlim(limits[maxrange])
            
        plt.show()
                
    
    def __del__(self):
        """ Delete figure when object handle is deleted or closed. """
        plt.close(self.fig)

    def clearlast(self,
                  removepoints=True, 
                  removeaxes=True,
                  removeframe=True):
        """ Remove previous plot"""
        if removepoints:
            self.points.remove()
        if removeaxes:
            for i in self.ellipaxes:
                i[0].remove()
        if removeframe:
            self.ellipframe.remove()
        plt.show()
