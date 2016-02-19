distellipsoid
=============

distellipsoid provides functons for fitting ellipsoids to crystallographic polyhedra, for the purpose of analysing distortion and volume changes,
irrespective of whether the changes occur from bond lengths or bond angles (or both). Typical usage is to read atom coordinates from a CIF 
(crystallographic information file) using EllipsoidGUI; start by calling EllipsoidGUI from the command line (once installed).

Alternatively, the program can be run on the command line by calling CIFellipsoid with arguments::

    CIFellipsoid CIF -m <poly centre> -r <max bond length> -l <ligand types>
    
This will produce an output file of ellipsoid parameters (CIF.TXT) and a 3D plot of the ellipsoid with a summary of useful ellipsoid parameters.
Many other options are also available; call `CIFellipsoid --help` for details.

Alternatively, the package can be imported and used as a python package::

    #!/usr/bin/env python
    import distellipsoid
    
    phases, plots = distellipsoid.calcellipsoid.calcfromcif([list of CIFs], [list of centres], **kwargs)
    
which will (by default) process all CIFs in parallel. kwargs are many of the options available to CIFellipsoid; most important are 
    * ligtypes or lignames (to specify correct ligands for centres)
    * radius (for bond searching)
    * tolerance (for fit tolerance)

Individual modules from the package can also be imported (ie. ellipsoid.py) for perform specific functions: read the documentation in the 
source code for more details.

CIFellipsoid script
===================

CIFellipsoid.py has a range of options for calculating ellipsoids from CIF files: help can be found by typing::

    python CIFellipsoid.py --help
    
The -m/--metal option can accept a list of site labels to test, but can also include regular expressions (e.g. `-m="Mn[0-4]?"` is equivalent to
`-m Mn0 Mn1 Mn2 Mn3 Mn4`. The quotes are necessary when reading in ranges (with '-') to prevent them from being read as script arguments, but
are not normally required.
The flag will also accept labels prepended with a '#' as sites to OMIT from testing. If only omitted sites are passed, all other sites will be
tested.

Note that when running with ipython, shell-like expansion of '*', ‘?’, ‘[seq]’ and ‘[!seq]’ is performed on arguments. To suppress this,
use TWO back slashes before the expansion (e.g. -m Mn\\* will find all sites starting Mn, even if files beginning with 'Mn' are present in the 
current directory). Passing `-G` after run will suppress ALL expansions.
    
Requirements
============

* Python version 2.7 (NOT Python 3)
* numpy (>=1.9.2)
* matplotlib (>= 1.4.3)
* PyCifRW (>= 3.3)
* multiprocessing (>=2.6.2.1)
* pandas (>=0.17.1)

Installation
============
    
Installation should work correctly with setuptools.py, including correctly installing all dependencies.

To install:
* Download this package
* Install using::
  python setup.py install
        
After installing, the package should be present in you default python Lib environment, and available for import/use.
CIFellipsoid and EllipsoidGUI should be directly available from your path

Testing
=======

The package contains some basic unit tests, which can be run with::
 python setup.py test

All tests should pass without exceptions - if not send me a bug report.

Disclaimer
==========

This software is provided as-is, on a best-effort basis. The authors accept no liabilities associated with the use of this software. 
It has been tested for accuracy of results for a number of cases, but only for uses that the authors can think of. We would be interested
to hear of any suggestions for new uses, or potential additions to the software.

We will attempt to correct any bugs as they are found on a best-effort basis!

Authors
=======

James Cumby - james.cumby@ed.ac.uk