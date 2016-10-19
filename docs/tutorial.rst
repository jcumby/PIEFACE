.. _tutorials:

Tutorials
=========

For most users, the simplest way to use |pieface|_ is using the graphical user interface |GUI|. This gives access to the most common features 
of |pieface|, and is operating-system independent. The underlying script is the same as the command line application |cmdprog|. For more advanced
use, |cmdprog| is recommended.

.. contents:: Contents
    :depth: 2
    :local:

Using the Grapical Interface (|GUI|)
------------------------------------

The main window
###############

To get started, open |GUI| either from a command prompt (type |GUI|) or (on Windows with the |pieface| installer) click the |GUI| icon on the desktop/start menu.
You should be confronted with a window similar to the following:

.. figure:: images/pieface_gui_labelled.*
    :align: center
    :alt: GUI opening screen
    :figclass: align-center
    :width: 2755
    :height: 2657
    :scale: 20
    
    |GUI| opening window.
    
The window contains the following elements:

    1) Input area
        Displays loaded CIF files, and allows files to be selected for display of results
    2) Output Log
        Displays calculation logs, useful for determining what options were used, and debugging problems
    3) :guilabel:`Add File(s)`
        Used to add CIF filoes for ellipsoid calculation
    4) :guilabel:`Remove File(s)`
        Can remove CIF files from the list
    5) :guilabel:`Plot Results`
        Displays an interactive plot of the calculated ellipsoids and summary of the key ellipsoid parameters for the selected CIF file(s)
    6) :guilabel:`Results Summary`
        Opens a summary of ellipsoid parameters for all calculated files - these can then be exported to a number of file formats
    7) Options for calculating ellipsoids
    8) Runs the calculation for all loaded CIF files

Command Options
###############
    
Once CIF files have been loaded (using button 3) the next step is to determine parameters for polyhedron determination and ellipsoid fitting (7). These are 
as follows:

    Polyhedron Centres
        These are the site labels (as specified in the CIF file) to be considered as the centre of a polyhedron. Exact labels can be given (e.g. ``Pr1 Pr2 Pr3 Pr4``)
        or regular expressions can also be used (``Pr*`` or ``Pr[1-4]``). To omit a label from the list, prepend the label with a ``#``, i.e. ``Pr* #Pr3`` will search 
        for all sites beginning ``Pr`` excluding ``Pr3``.
    
    Ligand Types
        This is a list of atom types (as defined in the CIF file) to treat as polyhedral ligands, i.e. ``O`` or ``O2-``. Wildcards are accepted.
        
    Ligand Labels
        This accepts a list of atom labels to treat explicitly as ligands, i.e. ``O1`` or ``O[1-3]``.
        
    .. note:: Ligand type/label specification can be specified together to create complex queries; if an atom is allowed by either label or type, it will be included 
        in the calculation unless it is specifically excluded (by the use of ``#``).
        
    Bond Radius
        The maximum centre-ligand distance to be considered part of the polyhedron.
        
    Fit tolerance
        The tolerance for the ellipsoid fit. In most cases the default should be acceptable (although can produce quite long calculation times).
        
    Number of processors
        The number of CIF files to be processed in parallel (should be <= the number of processors). Ignored if only one CIF file is loaded.
        
    Save results to file(s)
        If checked, this will save the resulting ellipsoid parameters to a text file for each CIF file.
        
    Process in parallel
        If checked, performs the calculation in parallel.
        
    Additional options
        This will accept some other non-standard options that can be supplied to |cmdprog|, but may not always work as expected.
        

.. note:: |GUI| is designed to process a large number of CIF files at once, which may not all contain the same atomic labels. If an atom label specified as either a 
    centre or ligand does not exist in a CIF file, it is therefore ignored. An error will be raised if a label is not present in *any* of the CIF files.
        
Running calculations
####################

Once CIF files are loaded and options supplied, calculations can be performed by clicking :guilabel:`Calculate All``. If a subset of CIF files are selected, the option is given to perform
the calculation only for those CIFs, keeping results for any other files.

.. warning:: Depending on the parameters chosen (particularly :guilabel:`Fit tolerance`) and complexity of the resulting ellipsoid, calculations can take a number of minutes per CIF file.
    Fit tolerance should not be reduced below 1E-9 to avoid problems with computational rounding errors

Viewing Results
###############

Ellipsoid Summary
^^^^^^^^^^^^^^^^^

Once calculations have been performed, the resulting ellipsoids can be viewed by selecting one or more CIF files in the input window, and clicking :guilabel:`Plot Results`. This will open 
a new window for each CIF file, with an summary of key ellipsoid parameters and an interactive plot of the ellipsoid:

.. figure:: images/pieface_ellipsoidplot.*
    :align: center
    :alt: Ellipsoid Summary
    :figclass: align-center
    :width: 685
    :height: 608
    :scale: 80
    
    Ellipsoid summary plot.

The ellipsoid image can be rotated by clicking and dragging in the window. Zooming can be achieved by right-clicking and dragging (at least on Windows).

.. note:: The ellipsoid is plotted using cartesian axes, with values in angstroms. The polyhedron centre is centred on the origin.

Parameter overview
^^^^^^^^^^^^^^^^^^

If calculations have been performed for multiple CIF files, it is often useful to compare results. Clicking ``Results Summary`` will open a new
window displaying a table of important ellipsoid parameters. If more than one polyhedron has been defined (e.g. more than one central atom) a separate
tab is produced for each polyhedron.

The :guilabel:`All data` table can be exported to a file by selecting :menuselection:`File --> Save As`.



Using the Command-line interface (|cmdprog|)
--------------------------------------------

|cmdprog| provides additional functionality beyond that of |GUI|. It can be started by typing |cmdprog| from a command prompt, or (if installed using the Windows installer) clicking on the |cmdprog|
icon on the start menu/desktop.

Full input details of the acceptable arguments to |cmdprog| can be found under :ref:`script_input`.

.. note:: If running |cmdprog| on Windows, processing a large number of CIF files can be simplified by using wildcard expansion: :command:`CIFellipsoid *.cif -m ...` will automatically
    process all cif files in the current folder
