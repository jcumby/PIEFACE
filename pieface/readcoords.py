""" Read in atomic coordinates and cell parameters """

from __future__ import division
import numpy as np
import os
#import warnings
import logging

# Set up logger
logger = logging.getLogger(__name__)

class Crystal(object):
    """ Class to hold crystal data and resulting ellipsoids. """
    def __init__(self, cell=None, atoms=None, atomtypes=None):
        """ Initialise class with cell parameters and atoms. """
        self._cell = {}
        self._atoms = {}
        self._atomtypes = {}
        self.cell = cell
        self.atoms = atoms
        self.polyhedra = []
        self.atomtypes = atomtypes

        #self.poly = {}
    @property
    def cell(self):
        return self._cell
    @cell.setter
    def cell(self, cell):
        """ Read in unit cell in range of formats (angles in degrees). """
        if cell is None:
            # Assume we are initialising
            self._cell = {}
        elif isinstance(cell, dict):
            # Read cell from dictionary
            if set(cell.keys()) == {'a','b','c','alp','bet','gam'}:
                self._cell['a'] = float(cell['a'])
                self._cell['b'] = float(cell['b'])
                self._cell['c'] = float(cell['c'])
                self._cell['alp'] = float(cell['alp'])
                self._cell['bet'] = float(cell['bet'])
                self._cell['gam'] = float(cell['gam'])
            elif set(cell.keys()) == {'a','b','c','alpha','beta','gamma'}:
                self._cell['a'] = float(cell['a'])
                self._cell['b'] = float(cell['b'])
                self._cell['c'] = float(cell['c'])
                self._cell['alp'] = float(cell['alpha'])
                self._cell['bet'] = float(cell['beta'])
                self._cell['gam'] = float(cell['gamma'])
            else:
                raise KeyError("Allowed keys for cell are a,b,c,alpha,beta,gamma")
        elif isinstance(cell, list):
            # Read cell from list [a,b,c,alpha,beta,gamma]
            if len(cell) != 6:
                raise ValueError("Unit cell parameters a,b,c,alpha,beta,gamma are required")
            self._cell['a'] = float(cell[0])
            self._cell['b'] = float(cell[1])
            self._cell['c'] = float(cell[2])
            self._cell['alp'] = float(cell[3])
            self._cell['bet'] = float(cell[4])
            self._cell['gam'] = float(cell[5])
        elif isinstance(cell, str):
            import re
            # Read cell parameters as string
            params = re.split('[,\t ]+', cell)
            if len(params) != 6:
                raise ValueError("Unit cell parameters a,b,c,alpha,beta,gamma are required (in that order)")
            self._cell['a'] = float(params[0])
            self._cell['b'] = float(params[1])
            self._cell['c'] = float(params[2])
            self._cell['alp'] = float(params[3])
            self._cell['bet'] = float(params[4])
            self._cell['gam'] = float(params[5])
    
    @property
    def atoms(self):
        return self._atoms
    @atoms.setter
    def atoms(self, atoms):
        """ Read atoms from dict """
        if atoms is None:   # we are initialising
            self._atoms = {}
            return
        for site in atoms:
            if isinstance(atoms[site], np.ndarray) or isinstance(atoms[site], list):
                self._atoms[site] = np.array(atoms[site]).astype(np.float)
            elif isinstance(atoms[site], string):
                self._atoms[site] = np.array(atoms[site].split()).astype(np.float)
            else:
                raise ValueError("Unknown data position type for atom {0}:\t{1}".format(site, type(atoms[site])))
    @property
    def atomtypes(self):
        return self._atomtypes
    @atomtypes.setter
    def atomtypes(self, atomtypes):
        """ Set atom types from dict """
        if atomtypes is None:   # Initialising
            self._atomtypes = {}
            return
        if len(atomtypes) == len(self.atoms):
            for site in atomtypes:
                self._atomtypes[site] = str(atomtypes[site])
        else:
            for site in self.atoms:
                try:
                    self._atomtypes[site] = str(atomtypes[ site.rsplit('_',1)[0]])
                except IndexError:
                    self._atomtypes[site] = str(atomtypes[ site ])      # Assume name has a '_' in it, and splitting broke the index
                
            
    def orthomatrix(self):
        """ Return orthogonalisation matrix from cell parameters."""
        # Orthogonalisation matrix (frac -> cart) with x along crystallographic a
        # [[a, b cos(gamma), c cos(beta)],
        # [ 0, b sin(gamma), (-c sin(beta) cos(alpha*)],
        # [ 0, 0, c sin(beta) sin(alpha*) ]]
        #
        # Usage: xyz = np.dot(M, abc)
        if self.cell is None:
            raise ValueError("Unit cell has not been defined")
        a = self.cell['a']
        b = self.cell['b']
        c = self.cell['c']
        salp = np.sin(np.radians(self.cell['alp']))
        sbet = np.sin(np.radians(self.cell['bet']))
        sgam = np.sin(np.radians(self.cell['gam']))
        calp = np.cos(np.radians(self.cell['alp']))
        cbet = np.cos(np.radians(self.cell['bet']))
        cgam = np.cos(np.radians(self.cell['gam']))
        V = a*b*c*(1 - calp**2 - cbet**2 - cgam**2 + 2*calp*cbet*cgam)**0.5
        #salpstar = V / (a*b*c*sbet*sgam)
        #sbetstar = V / (a*b*c*salp*sgam)
        #sgamstar = V / (a*b*c*salp*sbet)
        calpstar = (cbet*cgam - calp) / (sbet*sgam)
        cbetstar = (calp*cgam - cbet) / (salp*sgam)
        cgamstar = (calp*cbet - cgam) / (salp*sbet)
        salpstar = np.sqrt(1.0 - calpstar**2)
        
        M = np.array(\
            [[a, b*cgam, c*cbet ], \
            [ 0, b*sgam, -c*sbet*calpstar ], \
            [ 0, 0, c*sbet*salpstar ]]).astype(np.float64)
        return M
        
    def mtensor(self):
        """ Return metric tensor from cell parameters """
        # [[ a*a            , a*b*cos(gamma), a*c*cos(beta) ],
        #  [ a*b*cos(gamma) , b*b           , b*c*cos(alpha)],
        #  [ a*c*cos(beta)  , b*c*cos(alpha), c*c           ]]
        if self.cell is None:
            raise ValueError("Unit cell has not been defined")
        a = self.cell['a']
        b = self.cell['b']
        c = self.cell['c']
        calp = np.cos(np.radians(self.cell['alp']))
        cbet = np.cos(np.radians(self.cell['bet']))
        cgam = np.cos(np.radians(self.cell['gam']))
        return np.array([[ a*a      , a*b*cgam  , a*c*cbet], \
                         [ a*b*cgam , b*b       , b*c*calp], \
                         [ a*c*cbet , b*c*calp  , c*c     ]]).astype(np.float64)
        
    def makepolyhedron(self, centre, ligands, atomdict=None, ligtypes=None):
        """ Make polyhedron from centre and ligands. """
        import polyhedron
        # Polyhedron init is very flexible: this means it can be called with both atom labels
        # and a dict of positions (ie. self.atoms) or with individual dicts for centre and ligands.
        # This means that the polyhedron can be defined with ligand positions in a different 
        # position to that in self.atoms, for instance moved into an adjacent unit cell
        try:
            assert len(ligands) > 0
        except AssertionError:
            if isinstance(centre, dict):
                logger.warning("No ligands have been defined for %s", centre.keys()[0])
            elif isinstance(centre, tuple) or isinstance(centre, list):
                logger.warning("No ligands have been defined for %s", centre[0])
            else:
                logger.warning("No ligands have been defined for %s", centre)
        
        if isinstance(centre, dict):
            cenname = centre.keys()[0]
        elif isinstance(centre, tuple) or isinstance(centre, list):
            cenname = centre[0]
        elif isinstance(centre,str):
            cenname = centre
        setattr(self, str(cenname)+'_poly', polyhedron.Polyhedron(centre, ligands, atomdict=atomdict, ligtypes=ligtypes))
        self.polyhedra.append(cenname)
        
def readcif(FILE, phaseblock=None):
    """ Read useful data from cif using PyCifRW. """
    import CifFile     # Should be PyCifRW module, but also occurs in GSASII - I haven't yet found a conflict...
    import urllib
    
    symmops=None
    try:
        if os.path.isfile(FILE):
            allcif = CifFile.ReadCif(urllib.pathname2url(FILE))
        else:
            allcif = CifFile.ReadCif(FILE)
    except:
        if os.path.isfile(FILE):
            raise RuntimeError("There seems to be a problem with either {0} or PyCifRW!".format(FILE))
        else:
            raise IOError("Problem reading file {0} - does it exist?".format(FILE))
    
    if len(allcif.keys()) > 1:    # Cif file contains more than one entry
        logger.warning("CIF file contains multiple phases: {0}".format(", ".join(allcif.keys())))
        
        if phaseblock is None:
            # If no cif block is given, us the first (alphabetically)
            phase = sorted(allcif.keys())[0]
            logger.warning("Using phase {0}".format(sorted(allcif.keys())[0]))
        else:
            # Use provided phaseblock
            if phaseblock in allcif.keys():
                phase = phaseblock
                logger.warning("Using phase {0}".format(sorted(allcif.keys())[0]))
            else:
                matchblock = [s for s in allcif.keys() if phaseblock in s]
                if len(matchblock) == 1:
                    phase = matchblock[0]
                    logger.warning("Using phase {0}".format(matchblock[0]))
                elif len(matchblock) > 1:
                    logger.error("Phaseblock string matches multiple CIF entries")
                    raise ValueError("CIF phase definition matches multiple CIF entries")
                else:
                    logger.error("Phaseblock does not match any CIF entries")
                    raise ValueError("Phase definition string does not match any CIF entries")
        
    else:
        phase = allcif.keys()[0]
    
    # Read cell
    cell = {}
    
    cell['a'] = float(allcif[phase]['_cell_length_a'].split('(')[0])
    cell['b'] = float(allcif[phase]['_cell_length_b'].split('(')[0])
    cell['c'] = float(allcif[phase]['_cell_length_c'].split('(')[0])
    cell['alp'] = float(allcif[phase]['_cell_angle_alpha'].split('(')[0])
    cell['bet'] = float(allcif[phase]['_cell_angle_beta'].split('(')[0])
    cell['gam'] = float(allcif[phase]['_cell_angle_gamma'].split('(')[0])
    
    #Read in atom labels/coordinates
    atomcoords = {}
    atomtypes = {}
    for i,site in enumerate(allcif[phase]['_atom_site_label']):  # Iterate over all atom labels
        atomcoords[site] = np.array([ allcif[phase]['_atom_site_fract_x'][i].split('(')[0], allcif[phase]['_atom_site_fract_y'][i].split('(')[0], allcif[phase]['_atom_site_fract_z'][i].split('(')[0] ]).astype(np.float)
        atomtypes[site] = allcif[phase]['_atom_site_type_symbol'][i]
    
    
    for k in ['_symmetry_Int_Tables_number', '_space_group_IT_number']:
        spacegp = getattr(allcif[phase], k, 0)
    
    # Possible references to symmetry operations to check for
    symmop_strings = ['_space_group_symop_operation_xyz', '_symmetry_equiv_pos_as_xyz']
    keyintsec = set(symmop_strings) & set(allcif[phase].keys())
    if len( keyintsec ) < 1:
        raise KeyError("CIF file doesn't contain any symmetry operations")
        # Need to add function to generate symmops from spacegroup number
    else:
        symmops = allcif[phase][keyintsec.pop()]
        
    symmid_strings = ['_symmetry_equiv_pos_site_id']        # Valid keys for symmetry operation numbers from PyCifRW
    keyintsec = set(symmid_strings) & set(allcif[phase].keys())
    if len( keyintsec ) < 1:
        symmid = range(len(symmops))    # Number by default if needed
    else:
        symmid = allcif[phase][keyintsec.pop()]
        
    # Rearrange symmops so xyz is first
    validxyz = ['x, y, z', 'x,y,z', 'x y z']
    keyintsec = set(validxyz) & set(symmops)
    if len( keyintsec ) >= 1:
        idx = symmops.index( keyintsec.pop() )
        symmops.insert(0, symmops.pop(idx) )
        symmid.insert(0, symmid.pop(idx) )
    
    return cell, atomcoords, atomtypes, spacegp, symmops, symmid
    
def makeP1cell(atomcoords, symmops, symmid):
    """ Generate full unit cell contents from symmetry operations from Cif file

    Returned atom labels (as dict keys) are appended with '_##' to denote the number
    of the symmetry operation that generated them from cif file (initial position
    label is not changed).
    """
    
    def _shiftcoord((x,y,z)):
        """ Shift atom coordinates back into unit cell (0.0 <= r < 1.0)"""
        if x >= 1.0: x -= 1.0
        if x < 0.0: x += 1.0
        if y >= 1.0: y -= 1.0
        if y < 0.0: y += 1.0
        if z >= 1.0: z -= 1.0
        if z < 0.0: z += 1.0
        return x,y,z
        
    def _isspecial(site, xyz , newcoords):
        """ Check if site position already exists in newcoords (special position) """
        difftol = 1e-3  # Tolerance for difference in position (due to error reading eg 0.3333 from CIF file)
        
        for c in newcoords:
            if '_'.join(c.split('_')[:-1]) == site or c == site:     # Check if site name already exists in newcoords (allows for '_' in site name)
                if np.logical_or((abs(xyz - newcoords[c]) <= difftol), (abs(abs(xyz - newcoords[c])-1.0) <= difftol) ).all():
                    # Test if either sites are at same position (within tol) or at position (x,y,z)+1 (or -1)
                    return True
        return False
        
    
    newcoords = {}
    for site in atomcoords:     # Iterate over all atoms
        x,y,z = _shiftcoord(atomcoords[site])
        #print x,y,z
        for i, symm in enumerate(symmops):  # Iterate over symmops, counting them
            newx,newy,newz = _shiftcoord(eval(symm))     # Will fail with old-style division
            if _isspecial(site, np.array([newx, newy, newz]).astype(np.float), newcoords) and i != 0:   # Special position - don't add to list
                continue
            elif i == 0:    # First site, don't append '_1'
                newcoords[site] = np.array([newx, newy, newz]).astype(np.float)
            else:
                newcoords[site+"_{0:0{width}}".format(int(symmid[i]), width=len(str(len(symmops))))] = np.array([newx, newy, newz]).astype(np.float)
    return newcoords
    
def findligands(centre, atomcoords, orthom, radius=2.0, types=[], names = [], atomtypes=None):
    """ Find all atoms within radius of centre """
    # Calculate nearest neighbours by creating cell2 = cell1 + 99.5
    # then:
    # da = (a2 - a1) % 1 - 0.5
    # db = (b2 - b1) % 1 - 0.5
    # dc = (c2 - c1) % 1 - 0.5
    # To find nearest neighbour position, use X2 = x + dX etc...
    cell1 = atomcoords.copy()
    #cell2 = {}
    checktype=False
    checkname=False
    
    for site in cell1:
    #    cell2[site] = cell1[site] + 99.5
        # Check central atom exists
        if centre not in atomcoords.keys():
            raise KeyError("Atom {0} not found in atomcoords".format(centre))
    
    if types == []:
        checktype = False
    else:
        if atomtypes is None:
            raise ValueError("List of valid types requires corresponding atomtypes dictionary")
        for t in types:
            if t not in atomtypes.values():
                raise ValueError("Atom type {0} is not allowed. Valid types are: {1}".format(t, ", ".join([str(p) for p in set(atomtypes.values())])))
        checktype = True
    
    if names == []:
        checkname = False
    else:
        if atomtypes is None:
            raise ValueError("List of ligand names requires corresponding atomtypes dictionary")
        for t in names:
            if t not in atomtypes.keys():
                raise ValueError("Atom label {0} is not allowed. Valid labels are: {1}".format(t, ", ".join([str(p) for p in set(atomtypes.keys())])))
        checkname = True
        
    # Iterate over all atoms
    ligands = {}
    ligtypes = {}
    ligtypes[centre] = atomtypes[centre]
    
    #for site in cell2:
    for site in cell1:
        if site == centre:
            continue
        else:
            if checktype:   # Method to filter out correct atom types, either with exact name in dict, or original name in dict (without _##)
                if site in atomtypes.keys() and atomtypes[site] not in types:
                    continue
                elif '_'.join(site.split('_')[:-1]) in atomtypes.keys() and atomtypes[ '_'.join(site.split('_')[:-1]) ] not in types:
                    continue
            elif checkname: # Filter out ligands by label
                if site in atomtypes.keys() and ( site not in names and '_'.join(site.split('_')[:-1]) not in names):
                    continue
                elif '_'.join(site.split('_')[:-1]) in atomtypes.keys() and '_'.join(site.split('_')[:-1]) not in names:
                    continue
            
            # Array to check all 26 neighbouring cell translations (+ original cell)
            celltrans = np.array([[0,0,0],
                                  [1,0,0],[-1,0,0],
                                  [0,1,0],[0,-1,0],
                                  [0,0,1],[0,0,-1],
                                  [1,1,0],[1,-1,0],
                                  [-1,1,0],[-1,-1,0],
                                  [1,0,1],[1,0,-1],
                                  [-1,0,1],[-1,0,-1],
                                  [0,1,1],[0,1,-1],
                                  [0,-1,1],[0,-1,-1],
                                  [1,1,1],[1,1,-1],
                                  [-1,1,1],[-1,1,-1],
                                  [1,-1,1],[1,-1,-1],
                                  [-1,-1,1],[-1,-1,-1]])
            alltrans = cell1[site] + celltrans
            labelapp = 96   # Number to add character to name
            for t in (alltrans)[ np.linalg.norm(np.dot( orthom, (alltrans - cell1[centre]).T  ).T, axis=1 ) <= radius ]: # Find any translations within range
                #print site, t - cell1[centre], np.linalg.norm(np.dot( orthom, (t - cell1[centre]) ))
                if labelapp == 96:
                    ligands[site] = t
                    # Add ligand type
                    if site in atomtypes.keys():
                        ligtypes[site] = atomtypes[site]
                    elif '_'.join(site.split('_')[:-1]) in atomtypes.keys():
                        ligtypes[site] = atomtypes[ '_'.join(site.split('_')[:-1]) ]                    
                else:
                    ligands[site+chr(labelapp)] = t
                    # Add ligand type
                    if site in atomtypes.keys():
                        ligtypes[site+chr(labelapp)] = atomtypes[site]
                    elif '_'.join(site.split('_')[:-1]) in atomtypes.keys():
                        ligtypes[site+chr(labelapp)] = atomtypes[ '_'.join(site.split('_')[:-1]) ]
                labelapp += 1                    
            
            #########################
            # Old method using modulus division
            #########################
            # delabc = (cell2[site] - cell1[centre]) % 1 - 0.5    # Finds nearest neighbouring atoms, regardless of cell shifts - can fail for non-orthogonal crystal systems...
            # Check atom lies within radius
            #if np.linalg.norm(np.dot(orthom, delabc)) <= radius:
            #    ligands[site] = cell1[centre] + delabc
            #    if site in atomtypes.keys():
            #        ligtypes[site] = atomtypes[site]
            #    elif '_'.join(site.split('_')[:-1]) in atomtypes.keys():
            #        ligtypes[site] = atomtypes[ '_'.join(site.split('_')[:-1]) ]
                    
                # Need to also check if other translations are neighbours (ie. in small unit cells)
                # Translations for all 26 unit cells
                # celltrans = np.array([[1,0,0],[-1,0,0],
                                      # [0,1,0],[0,-1,0],
                                      # [0,0,1],[0,0,-1],
                                      # [1,1,0],[1,-1,0],
                                      # [-1,1,0],[-1,-1,0],
                                      # [1,0,1],[1,0,-1],
                                      # [-1,0,1],[-1,0,-1],
                                      # [0,1,1],[0,1,-1],
                                      # [0,-1,1],[0,-1,-1],
                                      # [1,1,1],[1,1,-1],
                                      # [-1,1,1],[-1,1,-1],
                                      # [1,-1,1],[1,-1,-1],
                                      # [-1,-1,1],[-1,-1,-1]])
                # alltrans = ligands[site] + celltrans
                # labelapp = 97   # Number to add character to name
                # for t in (alltrans)[ np.linalg.norm(np.dot( orthom, (alltrans - cell1[centre]).T  ).T, axis=1 ) <= radius ]: # Find any translations within range
                    # #print site, t - cell1[centre], np.linalg.norm(np.dot( orthom, (t - cell1[centre]) ))
                    # ligands[site+chr(labelapp)] = t
                    # # Add ligand type
                    # if site in atomtypes.keys():
                        # ligtypes[site+chr(labelapp)] = atomtypes[site]
                    # elif '_'.join(site.split('_')[:-1]) in atomtypes.keys():
                        # ligtypes[site+chr(labelapp)] = atomtypes[ '_'.join(site.split('_')[:-1]) ]
                    # labelapp += 1
    
    return ligands, ligtypes
                        
            
    