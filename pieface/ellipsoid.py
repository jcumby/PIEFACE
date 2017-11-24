"""
Module containing functions for calculating a minimum bounding ellipsoid from a set of points.

Contains a class to hold Ellipsoid object/properties, and functions to compute
the ellipsoid from a set of points

Basic usage:
    * Set up an Ellipsoid object
    * Assign a set of (cartesian) points to be used for fitting
    * Use method findellipsoid() to compute minimum bounding ellipsoid
    * After that, all other properties should be available.
"""

from __future__ import division
import numpy as np
import ellipsoid_algs


class Ellipsoid(object):
    """ An object for computing various hyperellipse properties. """
    def __init__(self, points=None, tolerance=1e-6):
        self.tolerance = tolerance
        self.radii = None   # Define radii as [r1 > r2 > r3], in that order
        self.centre = None
        self.rotation = None
        self.ellipdims = None
        self.points = points

        
    def getminvol(self, points=None, maxcycles=None):
        """ Find the minimum bounding ellipsoid for a set of points using the Khachiyan algorithm. 
        
        This can be quite time-consuming if a small tolerance is required, and ellipsoid axes
        lie a long way from axis directions.
        """
        # if set to a number, maxcycles will stop the calculation after that many iterations
        if points is None:
            try:
                points = self.points
            except AttributeError:
                raise
        
        if maxcycles is None:
            maxloops=0
        else:
            maxloops=int(maxcycles)
            
        ellipsoid_algs.khachiyan(points, self.tolerance, maxloops)
        # (N, d) = np.shape(points)
        # d = float(d)
    
        # # Q will be our working array
        # Q = np.vstack([np.copy(points.T), np.ones(N)]) 
        # QT = Q.T
        # # initialisations
        # err = 1.0 + self.tolerance
        # u = (1.0 / N) * np.ones(N)

        # count=0

        # # Khachiyan Algorithm
        # while err > self.tolerance:
            # V = np.dot(Q, np.dot(np.diag(u), QT))
            # M = np.diag(np.dot(QT , np.dot(np.linalg.inv(V), Q)))    # M the diagonal vector of an NxN matrix
            # j = np.argmax(M)
            # maximum = M[j]
            # step_size = (maximum - d - 1.0) / ((d + 1.0) * (maximum - 1.0))
            # new_u = (1.0 - step_size) * u
            # new_u[j] += step_size
            # err = np.linalg.norm(new_u - u)
            
            # if maxcycles is not None:
                # if count > maxcycles-1:
                    # self.tolerance = err
                    # break
            # u = new_u
            # count += 1
        #print "Converged with tolerance {0} in {1} iterations".format(loctol, count)


        # centre of the ellipse 
        centre = np.dot(points.T, u)
        # the A matrix for the ellipse
        A = np.linalg.inv(
                       np.dot(points.T, np.dot(np.diag(u), points)) - 
                       np.array([[a * b for b in centre] for a in centre])
                       ) / d
        # Get the values we'd like to return
        U, s, rotation = np.linalg.svd(A)
        radii = 1.0/np.sqrt(s)
        
        # rearrange matrices so r1>r2>r3
        P = np.array([[0,0,1],[0,1,0],[1,0,0]])
        U = np.fliplr(U)
        radii = radii[::-1]
        rotation = np.flipud(rotation)
        
        return (centre, radii, rotation)
        
    def findellipsoid(self, suppliedpts=None, **kwargs):
        """ Determine the number of dimensions required for hyperellipse, and call then compute it with getminvol. """

        if suppliedpts is not None:
            self.points = suppliedpts
        if self.points is None:
            raise AttributeError("Points have not been defined for object {0}".format(self))
        points = self.points
        
        relpoints = points - np.tile(points[0], (points.shape[0], 1))   # Coordinates of points relative to first point - needed for checking linearity and planarity
        
        if kwargs is not None:
            if 'maxcycles' in kwargs.keys():
                maxcycles = kwargs['maxcycles']
            else:
                maxcycles = None
        
        if self.numpoints() == 1:
            # Single ligand, ellipsoid is (fairly) meaningless
            self.radii = np.zeros(3)
            self.centre = points[0]
            self.rotation = np.eye(3)
            self.ellipdims = 0
            
        elif self.numpoints() == 2 or np.linalg.matrix_rank(relpoints) == 1:
            # Points are collinear - ellipsoid fitting will fail
            U,s,V = np.linalg.svd(relpoints)
            vector = V.T[:,0]     # Unit vector defining points
            linepoints = np.dot(U[:,:3], s)     # Coordinates of points in basis of vector
            self.radii = np.array([abs(max(linepoints) - min(linepoints))/2.,0.,0.])       # Should be s[0], but seems to be rounding errors
            self.centre = vector * self.radii[2] + points[0]
            self.rotation = V
            self.ellipdims = 1
            
        elif self.numpoints() == 3 or np.linalg.matrix_rank(relpoints) == 2:
            # Points are co-planar. Need to redefine coordinates in terms of plane for ellipsoid fitting
            U,s,V = np.linalg.svd(relpoints)
            planenorm = V.T[:,2]      # Vector normal to plane of points
            planepoints = np.dot(relpoints, V.T)[:,:2]     # 2D coordinates of points in plane
            centplane, radplane, rotplane = self.getminvol(planepoints, maxcycles=maxcycles)      # Values of ellipse in basis of plane
            #print centplane, radplane, rotplane
            self.radii = np.hstack([radplane, 0.])    # Radii are the same in both coordinate bases
            self.centre = np.dot( np.hstack([centplane, 0]), V) + points[0]
            rot3D = np.eye(3)
            rot3D[:2,:2] = rotplane
            self.rotation = np.dot(rot3D, V)   
            self.ellipdims = 2
            
        else:
            # Points occupy 3D space. Assume convex
            (cen,rad,rot) = self.getminvol(points, maxcycles=maxcycles)
            self.radii = np.array(rad)
            self.centre = cen
            self.rotation = rot
            self.ellipdims = 3

    @property
    def points(self):
        """ Points to define a hyperellipse. """
        if self._points is not None:
            return self._points
        else:
            raise AttributeError("No points have been assigned to ellipsoid")

    @points.setter
    def points(self, points):
        if isinstance(points, np.ndarray):
            pass
        elif points is None:      #Assume we are initialising
            self._points = points
            self.numpoints = None
            return
        elif isinstance(points, list):
            points = np.array(points)
        else:
            raise TypeError("Unknown data type {0}".format(type(points)))
        shape = points.shape
        # Receiving a numpy array
        if len(shape) > 2:
            raise ValueError("Points array cannot have more than 2 dimensions (passed {0})".format(len(shape)))
        self._points = points
        
    def numpoints(self):
        """ Return the number of points. """
        if self.points is not None:
            shape = self.points.shape
            if len(shape) == 1:
                return 1
            else:
                return shape[0]
        
    def meanrad(self):
        """ Return the mean radius. """
        if self.radii is not None:
            return np.mean(self.radii)
        else:
            raise AttributeError("Radii have not been defined: has an ellipsoid been fitted?")
    def radvar(self):
        """ Return variance of the radii. """
        if self.radii is not None:
            return np.mean((self.radii - self.meanrad())**2)
        else:
            raise AttributeError("Radii have not been defined: has an ellipsoid been fitted?")
    def raderr(self):
        """ Return standard deviation in radii """
        return np.sqrt(self.radvar())

    def sphererad(self):
        """ Return radius of sphere of equivalent volume as ellipsoid. """
        if self.radii is not None:
            if self.ellipdims < 3:
                return 0
            return self.radii.prod()**(1./3.)
        else:
            raise AttributeError("Radii have not been defined: has an ellipsoid been fitted?")
    
    def ellipsvol(self):
        """ Return volume of ellipsoid. """
        if self.radii is not None:
            if self.ellipdims < 3:
                return 0
            return 4./3.*np.pi*self.radii.prod()
        else:
            raise AttributeError("Radii have not been defined: has an ellipsoid been fitted?")
            
    def strainenergy(self):
        """ Return ellipsoid strain energy approximation. """
        if self.radii is not None:
            if self.ellipdims < 3:
                return np.nan       # Don't currently define it for non-3D shapes...
            if np.isclose(self.radii, np.zeros(self.ellipdims)).all():
                return float(0.0)
            return (self.radii**2).sum() / self.radii.sum()**2  - 1./3.
        else:
            raise AttributeError("Radii have not been defined: has an ellipsoid been fitted?")    
            
    def uniquerad(self, tolerance=None):
        """ Determine the number of unique radii within tolerance (defaults to self.tolerance)"""
        if self.radii is not None:
            if tolerance==None:
                tolerance = self.tolerance
            # unique = self.ellipdims
            # for i in range(self.ellipdims - 1):
                # for j in range(i+1,self.ellipdims):
                    # if abs(self.radii[i] - self.radii[j]) < tolerance:
                        # unique -= 1     # Radii are the same within tolerance, so reduce unique count
            # return unique
            if self.ellipdims == 0:
                return 0
            #elif self.ellipdims == 1:
            #    return 1
            else:
            #    radarr = np.vstack([self.radii]*3).T - self.radii
            #    unique = len( radarr[0][ abs(radarr[0]) >= tolerance ] )
             #   return unique + 1
                return np.count_nonzero( abs(np.diff(self.radii[ self.radii != 0. ])) >= tolerance) + 1
        else:
            raise AttributeError("Radii have not been defined: has an ellipsoid been fitted?")
        
    def plot(self, figure=None, axes=None, **kwargs):
        """ Plot graph of ellipsoid """
        import plotellipsoid
        ellipfig = plotellipsoid.EllipsoidImage(figure, axes)
        ellipfig.plotell(self, **kwargs)
        return ellipfig
        
    def centredisp(self):
        """ Return total displacement of centre. """
        return np.linalg.norm(self.centre)
        
    def centreaxes(self):
        """ Return displacement along ellipsoid axes. """
        if self.radii is not None:
            return np.dot(self.centre, self.rotation)
        else:
            raise AttributeError("Radii have not been defined: has an ellipsoid been fitted?")
    
    def shapeparam_old(self):
        """ Return ellipsoid shape measure r1/r2 - r2/r3. """
        if self.radii is not None:
            if self.ellipdims < 3:
                return np.nan
            return self.radii[0]/self.radii[1] - self.radii[1]/self.radii[2]
        else:
            raise AttributeError("Radii have not been defined: has an ellipsoid been fitted?")
    
    def shapeparam(self):
        """ Return ellipsoid shape measure r3/r2 - r2/r1. """
        if self.radii is not None:
            return self.radii[2]/self.radii[1] - self.radii[1]/self.radii[0]
        else:
            raise AttributeError("Radii have not been defined: has an ellipsoid been fitted?")
        
    def plotsummary(self, **kwargs):
        """ Plot graph of ellipsoid with text of basic parameters """
        import plotellipsoid
        
        if 'axcols' in kwargs.keys():       # Colours for ellipsoid axes
            if kwargs['axcols'] is None:
                axcols = ['b']*3
            else:
                axcols = kwargs['axcols']
        else:
            axcols = ['r','g','b']      
        
        if 'figure' in kwargs:
            ellipfig = plotellipsoid.EllipsoidImage(kwargs.pop('figure'), None)
        else:
            ellipfig = plotellipsoid.EllipsoidImage(None, None)
        
        
        ellipfig.fig.subplots_adjust(left=0.4)
        
        
        
        summary1 = "{0:^25}\n".format("Ellipsoid Summary") + \
                  "{0:^25}\n\n".format("-------------------") #+ \
        summary2 = "{:<12}:{:12.4f}\n".format("R1", self.radii[0]) #+ \
        summary3 = "{:<12}:{:12.4f}\n".format("R2", self.radii[1]) #+ \
        summary4 = "{:<12}:{:12.4f}\n".format("R3", self.radii[2]) + "\n" #+ \
        summary5 = "{:<10}{:<2}:{:12.4f}\n".format("Centre", "x", self.centre[0]) + \
                  "{:<10}{:<2}:{:12.4f}\n".format("","y", self.centre[1]) + \
                  "{:<10}{:<2}:{:12.4f}\n".format("","z", self.centre[2]) + \
                  "{:>10}{:<2}:{:12.4f}\n".format("Total","",self.centredisp()) + "\n" + \
                  "{:<12}:{:12.4f}\n".format("<R>", self.meanrad()) +\
                  "{:<12}:{:12.9f}\n".format("sigma(R)", self.raderr()) +\
                  "{:<12}:{:12.4f}\n".format("Volume", self.ellipsvol()) +"\n"+\
                  "{:<12}:{:12.4f}\n".format("S", self.shapeparam()) +"\n" +\
                  "{:<12}:{:12.9f}\n".format("Fit Error", self.tolerance)
        
        # Plot summary text on figure. Complexity is in order to match text colour with axis colour.
        text1 = ellipfig.fig.text(1-ellipfig.ax.get_position().x1-0.02, ellipfig.ax.get_position().y1, summary1, ha='left', verticalalignment='top', clip_on=True, fontname='monospace', fontsize=11)
        text1.draw(ellipfig.fig.canvas.get_renderer())
        text2 = ellipfig.fig.text(text1.get_window_extent().inverse_transformed(ellipfig.fig.transFigure).x0, text1.get_window_extent().inverse_transformed(ellipfig.fig.transFigure).y0, summary2, ha='left', verticalalignment='top', clip_on=True, fontname='monospace', fontsize=11, color=axcols[0])
        text2.draw(ellipfig.fig.canvas.get_renderer())
        text3 = ellipfig.fig.text(text2.get_window_extent().inverse_transformed(ellipfig.fig.transFigure).x0, text2.get_window_extent().inverse_transformed(ellipfig.fig.transFigure).y0, summary3, ha='left', verticalalignment='top', clip_on=True, fontname='monospace', fontsize=11, color=axcols[1])
        text3.draw(ellipfig.fig.canvas.get_renderer())
        text4 = ellipfig.fig.text(text3.get_window_extent().inverse_transformed(ellipfig.fig.transFigure).x0, text3.get_window_extent().inverse_transformed(ellipfig.fig.transFigure).y0, summary4, ha='left', verticalalignment='top', clip_on=True, fontname='monospace', fontsize=11, color=axcols[2])
        text4.draw(ellipfig.fig.canvas.get_renderer())
        text5 = ellipfig.fig.text(text4.get_window_extent().inverse_transformed(ellipfig.fig.transFigure).x0, text4.get_window_extent().inverse_transformed(ellipfig.fig.transFigure).y0, summary5, ha='left', verticalalignment='top', clip_on=True, fontname='monospace', fontsize=11)

        ellipfig.plotell(self, axcols=axcols, **kwargs)
        
        return ellipfig
                  
            

            
            
            
            
            
            
            
            
