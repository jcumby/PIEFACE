"""
Module for calculating distortion ellipsoids from polyhedra
"""

__author__ = "James Cumby"
__contact__ = "james.cumby@ed.ac.uk"
__license__ = "GPLv3+"
__copyright__ = "The University of Edinburgh, Edinburgh, UK"
__status__ = "Development"


__all__ = ["ellipsoid", "plotellipsoid", "readcoords", "polyhedron", "calcellipsoid", "writeproperties", "multiCIF"]

# Set up simple logging when importing as a module (should be separate to CIFellipsoid.py logging...)
import logging
logging.getLogger('distellipsoid').addHandler(logging.NullHandler())

import calcellipsoid
import readcoords
import writeproperties
import multiCIF