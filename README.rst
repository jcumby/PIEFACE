***********************************************************************************
Polyhedra Inscribing Ellipsoids For Analysis of Coordination Environments (PIEFACE)
***********************************************************************************

============
Introduction
============

**P**\ olyhedra **I**\ nscribing **E**\ llipsoids **F**\ or **A**\ nalysis of **C**\ oordination **E**\ nvironments (or PIEFACE) is an open source Python project for the
analysis of distortions in chemical coordination polyhedra.
The analysis is achieved using a minimum bounding ellipsoid (MBE) method; the smallest volume ellipsoid that can enclose all of the polyhedral vertices.
The result is very general, and is irrespective of polyhedron size or nature of the distortion. As such, the method has been applied to a range of crystallographic
situations.

For more details, see the `online documentation <http://pieface.readthedocs.io/>`_.

============
Installation
============

For detailed instructions, see `installation`_. On Windows, the easiest way is to download and run the most recent PIEFACE Windows Installer from `Downloads`_.

====================
License and Citation
====================

PIEFACE is open-source, distributed under an `MIT license <http://pieface.readthedocs.io/en/latest/license.html>`_.

Use of the software should cite the article:

    J. Cumby and J. P. Attfield, Ellipsoidal Analysis of Coordination Polyhedra, Nature Communications (2017).


=====
Usage
=====

---------
Basic Use
---------

PIEFACE is supplied with two utilities for easy use; a command-line program (``CIFellipsoid``) and a graphical interface (``EllipsoidGUI``).
These allow one or more CIF files to be read, coordination polyhedra to be determined, and ellipsoids to be fitted. The resulting ellipsoid
parameters can be saved to text file(s) and viewed interactively.

Once installed, the graphical interface can be started by typing ``EllipsoidGUI`` on the command line, or clicking the start menu icon (if installed using the `Windows Installer <Downloads>`_).

The command line application can be run by typing ``CIFellipsoid`` with appropriate arguments:

    CIFellipsoid CIF1 [CIF2 CIF3...] -m <polyhedron centre> -r <max bond length> -l <ligand types>
    
This will produce an output file of ellipsoid parameters (CIF.TXT) and a 3D plot of the ellipsoid with a summary of useful ellipsoid parameters.

Many other options are also available; type ``CIFellipsoid --help`` for details, open help from within ``EllipsoidGUI`` or see `Script Help`_.

------------
Advanced Use
------------

For more complex use cases, the package can be imported and used as a python package:

    import pieface
    
    phases, plots = distellipsoid.calcellipsoid.calcfromcif([list of CIFs], [list of centres], ``**``kwargs)

    
which will (by default) process all CIF files in parallel (as for the scripts). ``kwargs`` are many of the options available to ``CIFellipsoid``; most important are 
    
    * ligtypes or lignames (to specify correct ligands for centres)
    * radius (for bond searching)
    * tolerance (for fit tolerance)

Individual modules from the package can also be imported (ie. ``ellipsoid.py``) for perform specific functions: read the documentation in the
source code for more details or see the `API reference`_.

-------
Example
-------

See `Tutorials`_.

----
Help
----

Help can be accessed through:

    * `Online documentation <http://pieface.readthedocs.io/>`_
    * ``EllipsoidGUI`` from the help menu
    * ``CIFellipsoid --help``

=======
Testing
=======

The package contains some basic unit tests, which can be run with:
    
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

.. _docshome: http://pieface.readthedocs.io/
.. _introduction: http://pieface.readthedocs.io/en/latest/introduction.html
.. _Tutorials: http://pieface.readthedocs.io/en/latest/tutorial.html
.. _installation: http://pieface.readthedocs.io/en/latest/installation.html
.. _Downloads: https://github.com/jcumby/PIEFACE/releases
.. _Script Help: http://pieface.readthedocs.io/en/latest/script_input.html
.. _API reference: http://pieface.readthedocs.io/en/latest/api_reference.html
