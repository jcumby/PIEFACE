
==========================
Version 1.1.0
==========================

Major (API-breaking) changes:




Minor (backwards-compatible) changes:

- Modified readcoord.readcif to accept a `phaseblock` argument, to allow better reading of multi-phase CIF files.

Bug fixes:

- Changed readcoords.readcif so that if neither of `_symmetry_Int_Tables_number` or `_space_group_IT_number` is present, spacegroup 
  is set to 0. Does not currently affect any other routine in pieface.

==========================
Version 1.0.0 (2016-12-06)
==========================

First public release of PIEFACE!

Documentation is available at http://pieface.readthedocs.io/en/latest/