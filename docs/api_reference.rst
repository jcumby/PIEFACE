.. _api:

API Reference
*************

================
Ellipsoid Module
================

Contains the core functionality of |pieface|, responsible for fitting a :term:`MBE` to a set of points in Cartesian space.

.. automodule:: pieface.ellipsoid
    :members:
    
    
==========
Polyhedron
==========

Represents the set of objects that define a coordination polyhedron, including transforming from a unit cell description
to one of orthogonal (Cartesian) positions.

.. automodule:: pieface.polyhedron
    :members:
    
=======
Crystal
=======

Class to hold a number of polyhedron objects, as well as unit cell parameters and orthogonalisation matrix, etc.

.. autoclass:: pieface.readcoords.Crystal
	:members:
	
==============
Plot Ellipsoid
==============

Class to generate 3D interactive images of ellipsoids.

.. autoclass:: pieface.plotellipsoid.EllipsoidImage
	:members:
	
========================
CIF calculation routines
========================

.. _calcfromcif:

calcfromcif
-----------

.. autofunction:: pieface.calcellipsoid.calcfromcif

multiCIF
--------

The main module for computing ellipsoids from a number of files, using multiprocessing (one core per CIF file) if required. Largely contains routines for error checking 
input commands and calling :ref:`calcfromcif`.

.. automodule:: pieface.multiCIF
	:members:
	
=================
Utility Functions
=================

A number of utility functions are provided to simplify generation of polyhedra and reading/writing of files.


Unit Cell Functions
-------------------

.. autofunction:: pieface.readcoords.makeP1cell

.. autofunction:: pieface.readcoords.findligands

--------------
File Functions
--------------

.. autofunction:: pieface.readcoords.readcif

.. automodule:: pieface.writeproperties
	:members:
	
.. automodule pieface.calcellipsoid
	:members:
	
