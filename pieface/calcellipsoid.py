#!/usr/bin/env python

"""
Calculate minimum-bounding-ellipsoid for polyhedra, based on an imported Cif file.

This file can either be used as imported into Python (using calcfromcif)
or run as a script with appropriate arguments: in this case, the output routine
is also called to write data to a file.
"""

import sys
import logging
# Set up logger
logger = logging.getLogger(__name__)

def calcfromcif(CIF, centres, radius, allligtypes=[], alllignames=[], **kwargs):
    """ Main routine for computing ellipsoids from CIF file. """
    # kwargs should be valid arguments for polyhedron.makeellipsoid(), primarily designed for tolerance and maxcycles
    from pieface import readcoords
    
    logger.debug('Starting file %s', CIF)
    
    cell, atomcoords, atomtypes, spacegp, symmops, symmid = readcoords.readcif(CIF, getattr(kwargs, 'phase', 0))
    allatoms = readcoords.makeP1cell(atomcoords, symmops, symmid)
    
    phase = readcoords.Crystal(cell=cell, atoms=allatoms, atomtypes=atomtypes)
    
    for cen in centres:
        if cen not in allatoms.keys():
            logger.info("Centre %s is not present in atom labels: skipping", cen)
            continue
            
        validligtyps = list( set(allligtypes).intersection(set(atomtypes.values())))
        validlignames = list( set(alllignames).intersection(set(atomtypes.keys())))
        if len(validligtyps) == 0 and len(validlignames) == 0:
            raise ValueError("No ligands of type(s) or name(s) '{0}' are present in file {1}. Valid types are {2}".format(", ".join(allligtypes)+", ".join(alllignames), CIF, ", ".join([str(p) for p in set(atomtypes.values())])))
        elif len(validligtyps) != len(allligtypes):
            logger.info("Not all types %s are present in %s; using %s", ", ".join(allligtypes), CIF, ", ".join(validligtyps))
        elif len(validlignames) != len(alllignames):
            logger.info("Not all labels %s are present in %s; using %s", ", ".join(alllignames), CIF, ", ".join(validlignames))
        # Calculate ligands for current centre: the coordinates returned may be in a different unit cell to those in allatoms
        ligands, ligtypes = readcoords.findligands(cen, phase.atoms, phase.orthomatrix(), radius=radius, types=validligtyps, names=validlignames, atomtypes=phase.atomtypes)
        
        phase.makepolyhedron({cen:allatoms[cen]}, ligands, atomdict=None, ligtypes=ligtypes)
        
        polynm = cen+"_poly"
        
        getattr(phase, polynm).makeellipsoid(phase.orthomatrix(), **kwargs)
        
    logger.debug('Finishing file %s', CIF)    
    
    return phase
    
def makenesteddict(phases):
    """ Return dictionary of phases into nested dict CIF labels and ellipsoid parameters. 
    
    Dict structure is:
    {Central Atom Label : {Ellipsoid Parameter : Value } }
    """
    
    data = {}
    
    for site in set( [ j for file in phases.keys() for j in phases[file].polyhedra ] ):      # Iterate through all possible atom types in phases dict
        data[site] = {}
        data[site]['files'] = [ f for f in phases.keys() if site in phases[f].polyhedra ]     # Get list of files for which site is present
        
        #data[site]['radii'] = [ getattr(phases[f], site+"_poly").ellipsoid.radii for f in data[site]['files'] ]
        data[site]['r1'] = [ getattr(phases[f], site+"_poly").ellipsoid.radii[0] for f in data[site]['files'] ]
        data[site]['r2'] = [ getattr(phases[f], site+"_poly").ellipsoid.radii[1] for f in data[site]['files'] ]
        data[site]['r3'] = [ getattr(phases[f], site+"_poly").ellipsoid.radii[2] for f in data[site]['files'] ]
        data[site]['rad_sig'] = [ getattr(phases[f], site+"_poly").ellipsoid.raderr() for f in data[site]['files'] ]  
        data[site]['meanrad'] = [ getattr(phases[f], site+"_poly").ellipsoid.meanrad() for f in data[site]['files'] ]
        
        #data[site]['centre'] = [ getattr(phases[f], site+"_poly").ellipsoid.centre for f in data[site]['files'] ]
        data[site]['cenx'] = [ getattr(phases[f], site+"_poly").ellipsoid.centre[0] for f in data[site]['files'] ]
        data[site]['ceny'] = [ getattr(phases[f], site+"_poly").ellipsoid.centre[1] for f in data[site]['files'] ]
        data[site]['cenz'] = [ getattr(phases[f], site+"_poly").ellipsoid.centre[2] for f in data[site]['files'] ]
        data[site]['centredisp'] = [ getattr(phases[f], site+"_poly").ellipsoid.centredisp() for f in data[site]['files'] ]
        
        data[site]['coordination'] = [ getattr(phases[f], site+"_poly").ellipsoid.numpoints() - 1 for f in data[site]['files'] ]
        data[site]['shapeparam'] = [ getattr(phases[f], site+"_poly").ellipsoid.shapeparam() for f in data[site]['files'] ]
        data[site]['sphererad'] = [ getattr(phases[f], site+"_poly").ellipsoid.sphererad() for f in data[site]['files'] ]
        data[site]['ellipsvol'] = [ getattr(phases[f], site+"_poly").ellipsoid.ellipsvol() for f in data[site]['files'] ]
        data[site]['strainen'] = [ getattr(phases[f], site+"_poly").ellipsoid.strainenergy() for f in data[site]['files'] ]

        data[site]['cenr1'] = [ getattr(phases[f], site+"_poly").ellipsoid.centreaxes()[0] for f in data[site]['files'] ]
        data[site]['cenr2'] = [ getattr(phases[f], site+"_poly").ellipsoid.centreaxes()[1] for f in data[site]['files'] ]
        data[site]['cenr3'] = [ getattr(phases[f], site+"_poly").ellipsoid.centreaxes()[2] for f in data[site]['files'] ]

        data[site]['rotation'] = [ getattr(phases[f], site+"_poly").ellipsoid.rotation for f in data[site]['files'] ]
        
        data[site]['meanbond'] = [ getattr(phases[f], site+"_poly").averagebondlen(getattr(phases[f], 'mtensor')()) for f in data[site]['files'] ]
        data[site]['bondsig'] = [ getattr(phases[f], site+"_poly").bondlensig(getattr(phases[f], 'mtensor')()) for f in data[site]['files'] ]
        
        
    return data
    
def makeDataFrame(phases):
    """ Return Pandas DataFrame object, with CIF files as index and ellipsoid parameters as columns (hierarchical by centre atom)"""
    
    import pandas as pd
    from pieface.readcoords import Crystal
    
    if isinstance(phases, dict):
        if isinstance( phases[phases.keys()[0]], Crystal):      # We are reading a dict of Crystals: convert to nested dict first
            alldata = makenesteddict(phases)
        elif isinstance( phases[phases.keys()[0]], dict ):      # Looking at a dict of dicts: assume correct for pandas...
            alldata = phases
            
        d = dict([ (i, pd.DataFrame(alldata[i]).set_index('files')) for i in alldata.keys() ])        # Make dict of DataFrames
        
        frame = pd.concat(d, axis=1)
        
        if len(frame.index) == 1:   # We're looking at a single cif file - unstack DataFrame with atoms as index
            return frame.ix[frame.index[0]].unstack().apply(pd.to_numeric, errors='ignore')        # Need to convert back to float/int when unstacking
        else:
            return frame
    else:
        raise TypeError("Unknown data format for conversion to DataFrame (expected dict)")

if __name__ == "__main__":

    raise EnvironmentError("Please use CIFellipsoid.py script when running on the command line.")
        
    
        
        
        
        
        
        