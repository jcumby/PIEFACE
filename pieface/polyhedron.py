""" Module for containing polyhedron data and functions """

from __future__ import division
import numpy as np

class Polyhedron(object):
    """ Class to hold polyhedron object """
    def __init__(self, centre, ligands, atomdict=None, ligtypes=None):
        """ Initialise polyhedron object from sites/coordinates
        
        Can receive data in number of forms:
            - Sites as name/coordinates pairs in dict and nothing for atomdict
            - Sites as tuple of (name, [x,y,z]) as above (ligands occurring as list)
            or
            - Names of centre/ligands as strings, and dict of atomic names/coords in atomdict
            
            NOTE: abc refers to crystal coordinates, while xyz refers to cartesian
        """
        
        # __init__ sets parameters:
            # self.ligabc
            # self.cenabc
            # self.liglbl
            # self.cenlbl
            # self.allabc
            # self.alllbl
            # self.ligtyp
            # self.centyp
        
        if atomdict is None:
            # Receive atoms as name/coordinate pairs
            if isinstance(centre, dict):    # Centre atom first
                # Receive centre as dict
                if len(centre.keys()) != 1:
                    raise ValueError("Only one central atom must be defined")
                self.cenlbl = list(centre.keys())[0]
                self.cenabc = np.array(centre[self.cenlbl]).astype(np.float)
            elif isinstance(centre, tuple) or isinstance(centre, list):
                if len(centre) != 2:
                    raise ValueError("Only one central atom must be defined")
                else:
                    self.cenlbl = centre[0]
                    self.cenabc = np.array(centre[1]).astype(np.float)
            else:
                raise TypeError("Unknown central atom definition")
                
            if isinstance(ligands, dict):   # Read in ligands
                self.liglbl = [i for i in ligands.keys()]
                self.liglbl.sort()
                if len(ligands.keys()) == 0:
                    self.ligabc = np.array([[]]).T.astype(np.float) # Transpose so shape is (0,1) rather than (1,0)
                else:
                    self.ligabc = np.array([ ligands[i] for i in self.liglbl ]).astype(np.float)
            elif isinstance(ligands, list) or isinstance(ligands, tuple):
                if len(ligands) == 0:
                    self.liglbl = []
                    self.ligabc = np.array([[]]).T.astype(np.float) # Transpose so shape is (0,1) rather than (1,0)
                elif isinstance(ligands[0], list) or isinstance(ligands[0], tuple):
                    self.liglbl = [ i[0] for i in ligands ]
                    self.ligabc = np.array( [ i[1] for i in ligands ] ).astype(np.float)
                else:
                    raise TypeError("Unknown entry format for ligand {0}".format(ligands[0]))
            else:
                raise TypeError("Unknown ligands type {0}".format(type(ligands)))
        elif isinstance(atomdict, dict):
            # Receive atoms as name strings, with coordinates in atomdict
            if isinstance(centre, str) and len(centre) > 0:
                self.cenlbl = centre
                self.cenabc = np.array(atomdict[centre]).astype(np.float)
            else:
                raise TypeError("Incorrect type for central atom key ({0}) - expected string".format(type(centre)))
            if isinstance(ligands, list) or (ligands, tuple):
                self.liglbl = [ i for i in ligands ]
                if len(ligands) == 0:
                    self.ligabc = np.array([[]]).T.astype(np.float) # Transpose so shape is (0,1) rather than (1,0)
                else:
                    self.ligabc = np.array([ atomdict[i] for i in ligands ]).astype(np.float)
            elif isinstance(ligands, str):    # Assume there is just one ligand...
                self.liglbl = [ ligands ]
                self.ligabc = np.array([ atomdict[ligands] ]).astype(np.float)
        
        if self.ligabc.shape[0] != 0:        
            self.allabc = np.vstack([self.cenabc, self.ligabc])
        else:
            self.allabc = np.array([self.cenabc])
            
        if len(self.liglbl) != 0:
            self.alllbl = [self.cenlbl] + self.liglbl
        else:
            self.alllbl = [self.cenlbl]
        
        if ligtypes is not None:
            if isinstance(ligtypes, dict):
                try:
                    self.centyp = ligtypes[self.cenlbl]
                except:
                    self.centyp = None
                self.ligtyp = [ ligtypes[i] for i in self.liglbl ]
            elif isinstance(ligtypes, list) or isinstance(ligtypes, tuple):
                if len(ligtypes) == len(self.liglbl):
                    self.centyp = None
                    self.ligtyp = list(ligtypes)
                else:
                    self.centyp = ligtypes[0]
                    self.ligtyp = list(ligtypes[1:])
            else:
                raise TypeError("Unknown data format for ligand labels")
        else:
            self.centyp = None
            self.ligtyp = []
        
    def cenxyz(self, orthom):
        """ Return centre atom cartesian coordinates. """
        return np.dot(orthom, self.cenabc )
    def ligxyz(self, orthom):
        """ Return ligand cartesian coordinates. """
        if len(self.ligabc) != 0:
            return np.dot(orthom, self.ligabc.T ).T
        else:
            return np.array([[]])
    def allxyz(self, orthom):
        """ Return all atoms in cartesian coordinates. """
        return np.dot(orthom, self.allabc.T ).T
        
    def ligdelxyz(self, orthom):
        """ Return ligand cartesian coordinates relative to centre. """
        if len(self.ligabc) != 0:
            return self.ligxyz(orthom) - self.cenxyz(orthom) 
        else:
            return np.array([[]])
    def alldelxyz(self, orthom):
        """ Return all cartesian coordinates relative to centre. """
        return self.allxyz(orthom) - self.cenxyz(orthom)
    def ligdelabc(self):
        """ Return ligand coordinates relative to centre. """
        if len(self.ligabc) != 0:
            return self.ligabc - self.cenabc
        else:
            return np.array([[]])
    def alldelabc(self):
        """ Return all coordinates relative to centre. """
        return self.allabc - self.cenabc
        
    def allbondlens(self, mtensor):
        """ Return bond lengths to all ligands """
        # Use metric tensor to calculate vector magnitude
        if len(self.ligabc) != 0:
            return np.sqrt( np.diag( np.dot( np.dot(self.ligdelabc(), mtensor), self.ligdelabc().T )))
        else:
            return np.array([[]])
        
    def averagebondlen(self, mtensor):
        """ Return average centre-ligand bond length """
        return np.mean(self.allbondlens(mtensor))
        
    def bondlenvar(self, mtensor):
        """ Return variance of bond lengths """
        return np.mean((self.allbondlens(mtensor) - self.averagebondlen(mtensor))**2)
        
    def bondlensig(self, mtensor):
        """ Return standard deviation of bond lengths """
        return np.sqrt(self.bondlenvar(mtensor))
    
    def makeellipsoid(self, orthom, **kwargs):
        """ Set up ellipsoid object and fit minimum bounding ellipsoid """
        import ellipsoid
        
        if 'tolerance' in kwargs.keys():
            setattr(self, "ellipsoid", ellipsoid.Ellipsoid(points = self.alldelxyz(orthom), tolerance=kwargs.pop('tolerance')))
        else:
            setattr(self, "ellipsoid", ellipsoid.Ellipsoid(points = self.alldelxyz(orthom)))
        
        if 'maxcycles' in kwargs.keys():
            self.ellipsoid.findellipsoid(maxcycles=kwargs['maxcycles'])
        else:
            self.ellipsoid.findellipsoid()
            
    def pointcolours(self):
        """ Return a list of colours for points based on ligand type. """
        if len(self.ligtyp) == 0:
            return 'b'
        else:
            colourlist = ['r','g','c','m','y','k']
            c = 0
            colours = ['b']
            usedcols = {}
            if self.centyp is not None:
                usedcols[self.centyp] = colours[0]
            for i, site in enumerate(self.liglbl):
                if self.ligtyp[i] in usedcols.keys():
                    colours.append(usedcols[self.ligtyp[i]])
                elif self.centyp is not None and self.ligtyp[i] == self.centyp:
                    colours.append(usedcols[self.centyp])
                else:
                    try:
                        usedcols[self.ligtyp[i]] = colourlist[c]
                    except IndexError:      # Deal with too many ligand types
                        usedcols[self.ligtyp[i]] = 0 + 0.1*(c-len(colourlist)+1)
                    colours.append(usedcols[self.ligtyp[i]])
                    c += 1
                    
            return colours
            
            

