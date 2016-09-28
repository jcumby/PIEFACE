User-interface Documentation
****************************


===================
|cmdprog|
===================

This is the main command line script for using |pieface| to compute :term:`MBE` from one or more :term:`CIF` files.
Details of the input parameters are given below, or by typing |cmdprog| ``--help``.

.. ::
..	usage: CIFellipsoid [-h] [-o [OUTFILE [OUTFILE ...]]]
..						[-m CENTRES [CENTRES ...]] [-r RADIUS]
..						[-l [LIGTYPES [LIGTYPES ...]]]
..						[-n [LIGNAMES [LIGNAMES ...]]]
..						[-t TOLERANCE | --maxcycles MAXCYCLES] [-N] [-W]
..						[-P] [-U] [--procs [PROCS]] [--noplot]
..						[--writelog]
..						cifs [cifs ...]
 

.. program:: CIFellipsoid

.. cmdoption:: cifs

    Name(s) of CIF files to import as a space-delimited list. Can also accept valid web address(es).
    
.. cmdoption:: -m, --metal

    Site label(s) (as found in the CIF file) of polyhedron centres to analyse (e.g. Fe1).
	*Most* `regular expressions <https://docs.python.org/2/library/re.html>`_ can be used to make searching easier:
		:``Al*``:	matches any site label starting ``Al`` (``Al1``, ``Al2`` ... ``Al9999`` etc.)
		:``Al?``:	matches any label beginning `Al`, but only 3 characters in length (e.g. ``Al1`` - ``Al9``)
		:``Al[1-9]``:	matches any site ``Al1`` - ``Al9``
		
	In addition to most normal regular expressions, preceding any label by ``#`` will omit it from the search:
		:``#Al1``: will omit ``Al1`` from the list of acceptable centres.
		
	By combining these terms, it should be possible to specify most desired combinations.
	
.. cmdoption:: -o, --output

	Name(s) of output files to save results to. Default is <CIF Name>.txt.
	
.. cmdoption:: -r, --radius

	Maximum distance to treat a ligand as part of a polyhedron (default 3 Angstrom).
	
.. cmdoption:: -l, --ligandtypes

	Types of atom (as specified by CIF atom_type) to be considered as valid ligands (can use regular expressions).
	Default is all 	atom types.
	
.. cmdoption:: -n, --ligandnames

	Atom labels to use as ligands (same syntax as --metal). By default, any ligand allowed by --ligandtypes is allowed.
	The combination of --ligandtypes and --ligandnames is taken as an ``AND``-like operation, such that sites are only 
	excluded if done so explicitly.
	
.. cmdoption:: -t, --tolerance

	Tolerance to use for fitting ellipsoid to points (default 1e-6).
	
.. cmdoption:: --maxcycles
	
	Maximum number of iterations to perform for fitting (default infinite).
	
.. cmdoption:: -N

	Don't save results to text files
	
.. cmdoption:: -W, --overwriteall

	If existing results files already exist, force |pieface| to overwrite them all.
	
.. cmdoption:: -P, --PrintLabels

	Print all valid site labels for each CIF file supplied.
	
.. cmdoption:: -U, --Unthreaded

	Turn off parallel processing of CIF files.
	
.. cmdoption:: --procs

	Number of processors to use for parallel processing (default all).
	
.. cmdoption:: --noplot

	Don't produce interactive ellipsoid images after calculation.
	
.. cmdoption:: --writelog

	Write a debugging log to ``debug.log``.
	



	
    