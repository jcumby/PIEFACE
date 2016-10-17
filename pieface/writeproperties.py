""" Module to write pieface ellipsoid parameters to text file. """

from __future__ import division
import os, sys
import numpy as np
import textwrap
import logging
from time import sleep

# Set up logger
logger = logging.getLogger(__name__)

# Basic Format definitions
fmt_flt = "{:11.6f}"
fmt_lflt = "{:14.8f}"
fmt_str = "{:<11}"
fmt_lstr = "{:<14}"
fmt_vlstr = "{:<25}"
fmt_int = "{:11d}"
fmt_lint = "{:14d}"
fmt_3colstr = "{:<33}"
fmt_vlrstr = "{:>25}"

# Combined formatters based on simple definitions above
fmt_unitcell = fmt_flt*6+"\n"
fmt_atm_cord = fmt_str+fmt_flt*3+"\n"
fmt_llbl_1lflt = fmt_vlstr+":"+fmt_lflt+"\n"
fmt_llbl_3lflt = fmt_vlstr+":"+fmt_lflt+fmt_lflt+fmt_lflt+"\n"
fmt_llbl_1lint = fmt_vlstr+":"+fmt_lint+"\n"

fmt_lbl_9flt_str = fmt_str+fmt_flt*9+fmt_vlrstr+"\n"
fmt_lbl_10flt = fmt_str+fmt_flt*10+"\n"
fmt_lbl_3flt = fmt_str+fmt_flt*3+"\n"
fmt_lbl_3flt_str = fmt_str+fmt_flt*3+fmt_vlrstr+"\n"

def _writeintro(fileob, v=0):
    """ Write ellipsoid properties to file. """
    
    if v == 1:
        string = """\
                # Introduction to the ellipsoid method, perhaps also
                # a reference?
                  
                """
        fileob.write(textwrap.dedent(string))
    
    if v == 6:
        string = """\
                # A longer introduction to the ellipsoid method,
                # as well as more detail about the parameters 
                # reported? And a reference?
                  
                """
        fileob.write(textwrap.dedent(string))
    
def _writecrystal(fileob, phase, v=0):
    """ Write Crystal data to file. """
    
    if v >= 1:
        fileob.write("! Unit cell parameters a b c alpha beta gamma\n")
        fileob.write((fmt_unitcell).format(phase.cell['a'],phase.cell['b'],phase.cell['c'],phase.cell['alp'], phase.cell['bet'], phase.cell['gam']))
        fileob.write("\n")
    
    if v >= 4:
        fileob.write("! Coordinates of all atoms in unit cell ({0})\n".format(len(phase.atoms)))
        for site in phase.atoms:
            fileob.write(fmt_atm_cord.format(site, *phase.atoms[site]))
        fileob.write("\n")
    
def _writepolyhedron(fileob, phase, cen, v=0):
    """ Write details of polyhedron definition """
    polyob = getattr(phase, cen+"_poly")
    
    if v == 0:
        # Assume we don't want any lists of ligands or coordinates
        pass
    
    if v == 1:  
        fileob.write("! Polyhedron definition {0} ({1}-coordinate) -------\n".format(cen, len(polyob.liglbl)))
        fileob.write((fmt_str+fmt_3colstr+"\n").format("# Atom", "Lattice Coords"))
        data = [cen] + [p for p in polyob.cenabc] + ["*Central Site"]
        fileob.write(fmt_lbl_3flt.format(*data))
        for i, lig in enumerate(polyob.liglbl):    # Iterate over all sites
            data = [lig] + [p for p in polyob.ligabc[i]]
            fileob.write(fmt_lbl_3flt.format(*data))
        fileob.write("\n")        
        
    if v >= 2:
        fileob.write("! Polyhedron definition {0} ({1}-coordinate) -------\n".format(cen, len(polyob.liglbl)))
        fileob.write((fmt_str+fmt_3colstr*3+fmt_vlrstr+"\n").format("# Atom", "Lattice Coords","CartesianCoords","CartesianCoordsReltoCentre","Centre-ligand bondlength"))
        data = [cen] + [p for p in polyob.cenabc] + [p for p in polyob.cenxyz(phase.orthomatrix())]
        data = data + [ p for p in polyob.alldelxyz(phase.orthomatrix())[0]] + ["*Central Site"]
        fileob.write(fmt_lbl_9flt_str.format(*data))
        for i, lig in enumerate(polyob.liglbl):    # Iterate over all sites
            data = [lig] + [p for p in polyob.ligabc[i]] + [p for p in polyob.ligxyz(phase.orthomatrix())[i]] + [ p for p in polyob.ligdelxyz(phase.orthomatrix())[i]] + [ polyob.allbondlens(phase.mtensor())[i] ]
            fileob.write(fmt_lbl_10flt.format(*data))
        fileob.write("\n")
    
def _writeellipsoid(fileob, phase, cen, v=0):
    """ Write paramters of fitted ellipsoid """
    ellipob = getattr(phase, cen+"_poly").ellipsoid
    
    if v >= 0:
        fileob.write("! Ellipsoid parameters {0} -------\n".format(cen))
        fileob.write(fmt_llbl_3lflt.format("Radii R1 > R2 > R3", *ellipob.radii))
        fileob.write(fmt_llbl_3lflt.format("Ellipsoid centre x,y,z", *ellipob.centre))

    if v >= 1:
        fileob.write(fmt_llbl_3lflt.format("Rotation matrix", *ellipob.rotation[0]))
        fileob.write(fmt_llbl_3lflt.format("", *ellipob.rotation[1]))
        fileob.write(fmt_llbl_3lflt.format("", *ellipob.rotation[2]))
    
    if v >= 2:
        fileob.write(fmt_llbl_1lflt.format("Tolerance", ellipob.tolerance))
        fileob.write(fmt_llbl_1lflt.format("Mean Radius", ellipob.meanrad()))
        fileob.write(fmt_llbl_1lflt.format("Radius Variance", ellipob.radvar()))
        fileob.write(fmt_llbl_1lflt.format("Volume", ellipob.ellipsvol()))
    
    if v >= 3:    
        fileob.write(fmt_llbl_1lint.format("Hyperellipse dims", ellipob.ellipdims))    
        fileob.write(fmt_llbl_1lint.format("Unique radii", ellipob.uniquerad()))
        fileob.write(fmt_llbl_1lflt.format("Equiv. Sphere Radius", ellipob.sphererad()))
        fileob.write(fmt_llbl_1lflt.format("Strain Energy", ellipob.strainenergy()))
        fileob.write(fmt_llbl_1lflt.format("Shape Parameter", ellipob.shapeparam()))
    
    if v >= 0:
        fileob.write('\n')

    
def _query(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer. """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'".format(default))

    while True:
        #print question + prompt
        logger.critical(question + prompt)
        sleep(1)    # Sleep briefly to allow logger to output last message
        choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            logger.critical("Please respond with 'yes' or 'no' (or 'y' or 'n').\n")
    
def writeall(FILE, phase, verbosity=3, overwrite=False):
    """ Write data to file 
    
    Increasing verbosity above 0 will increase the amount of data printed to file
    (4 is maximum output)
    """
    
    if not overwrite:
        while True:
            if os.path.isfile(FILE):
                if not _query("File {0} already exists: do you want to overwrite it?".format(FILE), default="no"):
                    logger.critical("Enter new filename ([Return] to exit):\t")
                    sleep(1)    # Sleep briefly to allow logger to output last message
                    #newout = raw_input("Enter new filename ([Return] to exit):\t")
                    newout = raw_input()
                    if newout == "":
                        return
                    else:
                        FILE = newout
            break
    
    try:
        fileob = open(FILE, "w")
    except IOError as e:
        logger.critical("I/O error({0}): {1}".format(e.errno, e.strerror))
      
    logger.debug("Output written to {0}".format(FILE))

    _writeintro(fileob, v=verbosity)
    _writecrystal(fileob, phase, v=verbosity)
    for site in phase.polyhedra:
        _writepolyhedron(fileob, phase, site, v=verbosity)
        _writeellipsoid(fileob, phase, site, v=verbosity)
    
    fileob.close()
    
        