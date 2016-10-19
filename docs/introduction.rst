.. _introduction:

Introduction to PIEFACE
***********************

=========================================================================
Polyhedra Inscribing Ellipsoids For Analysis of Coordination Environments
=========================================================================


**P**\ olyhedra **I**\ nscribing **E**\ llipsoids **F**\ or **A**\ nalysis of **C**\ oordination **E**\ nvironments (or |pieface|_) is an open source |Python|_ project intended for the
analysis of distortions of a chemical coordination polyhedron. The analysis is very general, irrespective of polyhedron size or nature of the distortion, and could be applied
to any problem where a coordination sphere with known coordinates exists, from extended inorganic solids to organic molecules. 
Full details of the method can be found in the original research article, |article|_, including some interesting examples.

For many crystallographic polyhedra, distortion is difficult to rationalise simply in terms of deviations of bond lengths or bond angles from *ideal* values. By fitting the smallest volume :term:`ellipsoid`
around the polyhedron, distortions are defined in terms of the three principal axes of the ellipsoid and it's orientation in space. The distortion of this :term:`ellipsoid` can then give a simple description
of the distortions involved.

.. _citelink:

Citing |pieface|
================

If you use |pieface|, please **cite** it:

    |citation|_


===============
Getting Started
===============

Once installed (see :ref:`installation`) |pieface| can be accessed either through a command-line interface (|cmdprog|) or a user-friendly graphical interface (|GUI|). 
Both should be available on the system command line/terminal, and also from the start menu (if installed using the Windows installer).

|GUI|
    Should be adequate for most users. This :term:`GUI` provides a clickable interface to commonly used |pieface|_ functions, and allows users to
    import :term:`CIF` files for analysis, and examine/save the resulting output.
|cmdprog|
    Gives terminal-based access to a wider range of capabilities, details of which can be found by typing |cmdprog| ``--help``.

    
In both cases, the input required is one or more :term:`CIF` files, and a list of atom types or labels to be used as polyhedron centres and ligands. 
Once calculated (which can take some time for a large number of files) the resulting ellipsoid parameters are saved as a text file (one per :term:`CIF` file).
The resulting ellipsoids and parameters can also be visualised interactively.

More detailed examples of usage can be found in :ref:`tutorials`.

=======
License
=======

|pieface| is distributed under the :ref:`MIT license <license>`. Any use of the software should be :ref:`cited <citelink>`.

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


