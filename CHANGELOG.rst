
==========================
Version 1.1.0
==========================

Major (API-breaking) changes:

- Modified readcoord.readcif to accept a `phaseblock` argument, to allow better reading of multi-phase CIF files.
- Tests are now controlled by pytest, rather than unittest

Minor (backwards-compatible) changes:

- Changed readcoords.readcif so that if neither of `_symmetry_Int_Tables_number` or `_space_group_IT_number` is present, spacegroup 
  is set to None. Does not currently affect any other routine in pieface.
- Added update-check to CIFellipsoid and EllipsoidGUI to check for newer versions of PIEFACE.
- Minor updates to documentation and code organisation

==========================
Version 1.0.0 (2016-12-06)
==========================

First public release of PIEFACE!

Documentation is available at http://pieface.readthedocs.io/en/latest/