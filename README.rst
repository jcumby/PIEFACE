***********************************************************************************
Polyhedra Inscribing Ellipsoids For Analysis of Coordination Environments (PIEFACE)
***********************************************************************************

============
Introduction
============

**P**\ olyhedra **I**\ nscribing **E**\ llipsoids **F**\ or **A**\ nalysis of **C**\ oordination **E**\ nvironments (or pieface) is an open source Python project for the
analysis of distortions in chemical coordination polyhedra.
The analysis is achieved using a minimum bounding ellipsoid (MBE) method; the smallest volume ellipsoid that can enclose all of the polyhedral vertices.
The result is very general, and is irrespective of polyhedron size or nature of the distortion. As such, the method has been applied to a range of crystallographic
situations.

============
Installation
============

See `installation`_. On Windows, the easiest way is to download and run the self-contained `pieface installer`_

====================
License and Citation
====================

pieface is open-source, distributed under an [MIT license](license.txt).

Use of the software should cite the following article:

[REFERENCE](http://www.csec.ed.ac.uk)

=====
Usage
=====

---------
Basic Use
---------

pieface is supplied with two utilities for easy use; a command-line program (`CIFellipsoid`) and a graphical interface (`EllipsoidGUI`).
These allow one or more CIF files to be read, coordination polyhedra to be determined, and ellipsoids to be fitted. The resulting ellipsoid
parameters can be saved to text file(s), or viewed within `EllipsoidGUI`.

Once installed, the graphical interface can be started by typing `EllipsoidGUI` on the command line, or clicking the start menu icon (if using the Windows executable).

The command line application can be run by typing `CIFellipsoid` with appropriate arguments:

    CIFellipsoid CIF1 [CIF2 CIF3...] -m <polyhedron centre> -r <max bond length> -l <ligand types>
    
This will produce an output file of ellipsoid parameters (CIF.TXT) and a 3D plot of the ellipsoid with a summary of useful ellipsoid parameters.

Many other options are also available; type `CIFellipsoid --help` for details, or open help from within `EllipsoidGUI`.

------------
Advanced Use
------------

For more complex use cases, the package can be imported and used as a python package:

    import pieface
    
    phases, plots = distellipsoid.calcellipsoid.calcfromcif([list of CIFs], [list of centres], **kwargs)
    
which will (by default) process all CIF files in parallel (as for the scripts). `kwargs` are many of the options available to CIFellipsoid; most important are 
    * ligtypes or lignames (to specify correct ligands for centres)
    * radius (for bond searching)
    * tolerance (for fit tolerance)

Individual modules from the package can also be imported (ie. ellipsoid.py) for perform specific functions: read the documentation in the
source code for more details.

-------
Example
-------

See `tutorial`_

=======
Testing
=======

The package contains some basic unit tests, which can be run with::
 python setup.py test

All tests should pass without exceptions - if not please send me a bug report.

==========
Disclaimer
==========

This software is provided as-is, on a best-effort basis. The authors accept no liabilities associated with the use of this software. 
It has been tested for accuracy of results for a number of cases, but only for uses that the authors can think of. We would be interested
to hear of any suggestions for new uses, or potential additions to the software.

We will attempt to correct any bugs as they are found on a best-effort basis!

=======
Authors
=======

James Cumby - james.cumby@ed.ac.uk

.. _tutorial: docs/tutorial.rst
.. _installation: docs/installation.rst
.. _installer: ../downloads/WinSetup_PIEFACE_0.3.0.0.exe