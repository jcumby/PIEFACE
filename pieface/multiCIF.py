"""
Module for processing one or more CIF files using supplied options
To run from the command line, call the CIFellipsoid.py script.
"""


import logging, sys, os
import multiprocessing
from pieface import writeproperties, calcellipsoid
import argparse
import os, sys
import re

# Set up root logger
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
  
class KeyboardInterruptError(Exception): pass

class QueueHandler(logging.Handler):
    """
    This is a logging handler which sends events to a multiprocessing queue.
    The plan is to add it to Python 3.2, but this can be copy pasted into
    user code for use with earlier Python versions.
    """
    def __init__(self, queue):
        """
        Initialise an instance, using the passed queue.
        """
        logging.Handler.__init__(self)
        self.queue = queue
    def emit(self, record):
        """
        Emit a record.
        Writes the LogRecord to the queue.
        """
        try:
            ei = record.exc_info
            if ei:
                dummy = self.format(record) # just to get traceback text into record.exc_text
                record.exc_info = None  # not needed any more
            self.queue.put_nowait(record)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)

def worker_configure(queue):
    """ Initialise logging on worker"""
    ## Can be used to turn off passing of CTRL-C to sub-processes, but then 
    ## parent has to wait for current files to finish before killing...
    #import signal
    #signal.signal(signal.SIGINT, signal.SIG_IGN)
    
    h = QueueHandler(queue) # Just the one handler needed
    root = logging.getLogger()
    root.addHandler(h)
    root.setLevel(logging.DEBUG) # send all messages, for demo; no other level or filter logic applied.    
    root.info('Starting processing on %s', str(multiprocessing.current_process().name))

def listener_configurer(name=None):
    """ Function to configure logging output from sub processes"""
    root = logging.getLogger()

    # Set up handler for all debug output
    h = logging.FileHandler('./debug.log', mode='w')
    #h = logging.StreamHandler(sys.stdout)
    f = logging.Formatter('%(name)-40s %(funcName)-20s %(processName)-13s %(levelname)-8s %(message)s')
    h.setFormatter(f)
    root.addHandler(h)
    root.setLevel(logging.DEBUG)
    
    # # Set up logging for main script - print to stdout
    p = logging.StreamHandler(sys.stdout)
    q = logging.Formatter('%(asctime)s %(processName)-20s %(name)-30s %(levelname)-8s %(message)s', "%Y-%m-%d %H:%M:%S")
    p.setFormatter(q)
    # #p.addFilter(InfoFilter())
    # #p.addFilter(CritFilter())
    p.setLevel(logging.DEBUG)
    root.addHandler(p)

def listener_empty_config(name=None):
    """ Empty listener configurer, to do nothing except pass logs directly to parent"""
    return
    
def listener_process(queue, configurer):
    """ Process waits for logging events on queue and handles then"""
    configurer()
    while True:
        try:
            record = queue.get()
            if record is None: # We send this as a sentinel to tell the listener to quit.
                break
            logger = logging.getLogger(record.name)
            logger.handle(record) # No level or filter logic applied - just do it!
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            import sys, traceback
            print >> sys.stderr, 'Whoops! Problem:'
            traceback.print_exc(file=sys.stderr)
    
def _wrapper(args):
    """ Wrapper function for passing arguments to calcfromcif when multiprocessing """
    from pieface import calcellipsoid
    try:
        return calcellipsoid.calcfromcif(args[0], args[1], args[2], allligtypes=args[3], alllignames=args[4], maxcycles=args[5], tolerance=args[6], phase=args[7])
    except IOError as e:    # Except IOErrors so that missing files are handled sensibly...
        return e
    except KeyboardInterrupt:
        raise KeyboardInterruptError()
        
def _alllabels(CIF, phase=None):
    """ Return all allowed labels in CIF file. """
    return _alltyplbls(CIF, phase).keys()

def _alltyplbls(CIF, phase=None):
    """ Return all allowed labels and corresponding types in CIF file. """
    from pieface.readcoords import readcif
    cell, atomcoords, atomtypes, spacegp, symmops, symmid = readcif(CIF, phase)
    # Just return atomtypes dict {label: type} direct from readcif
    return atomtypes
    
def _alltypes(CIF, phase=None):
    """ Return all allowed types in CIF file. """
    return _alltyplbls(CIF, phase).values()
    
def check_labels(labels, alllabs):
    """ Check that all labels are present in all cif files, handling regular expressions if needed.
    Returns
    -------
    list of labels to test,
    list of labels to omit,
    list of missing labels
    """
    
    test = set()
    omit = set()
    missing = set()
    
    for l in labels:
        # Iterate over labels, either adding to `test` or `omit` sets
        if any( [i in l for i in ['*','$','^','.','?','{','}','|','[',']','\\']] ):
            # Treat label as regex (approximately)
            if l[0] == '#':     # omit label l
                found = False
                for a in alllabs:
                    if re.search(l[1:], a):     # Regex matches
                        omit.add(a)
                        found = True
                if not found:
                    # omitted label did not occur in any file
                    missing.add(l)
            else:           # Find centres based on regex       
                found = False
                for a in alllabs:
                    if re.search(l, a):     # Regex matches
                        test.add(a)
                        found = True
                if not found:
                    # label not present in any file
                    missing.add(l)
        elif l[0] == '#':      # Omit centre with # prepending name
            if l[1:] in alllabs:
                omit.add(l[1:])
            else:
                missing.add(l)
            continue
        else:
            if l in alllabs:
                test.add(l)
            else:
                missing.add(l)
                
    return list(test), list(omit), list(missing)            

 
def check_centres(cifs, centres, phase=None):
    """ Determine which centres to use based on CIF contents and user-supplied arguments."""
    # Work out what centres to include
    log.debug('Checking centre labels')
    
    allcentres = set([ i for c in cifs for i in _alllabels(c, phase) ])
    testcen, omitcen, missingcen = check_labels(centres, allcentres)
    
    if len(missingcen) > 0:
        log.warning("Centres %s are not valid labels for any CIF files; they will be skipped", str(", ".join(missingcen)))
    
    if len(testcen) == 0:       # Empty list was passed apart from exclusions: add all atoms apart from those
        testcen = allcentres.copy()
        testcen.difference_update(omitcen)
        
    if not set(testcen).issubset(allcentres):
        log.critical("Label(s) %s are not present in any of the CIF files - stopping", str(" ".join([str(i) for i in set(testcen).difference(allcentres)])))
        log.critical("Valid atom labels are:\n")
        for CIF in cifs:
            log.critical("%-40s:  %s", CIF, ", ".join(_alllabels(CIF, phase)))
        return None
 
    return testcen
    
def check_ligands(cifs, ligtypes, liglbls, phase=None):
    """ Find lists of ligand labels and types that should be used to define ellipsoids based on supplied lists.

    NOTE: This function will find the appropriate combination of label/type commands to find all required ligands,
          EXCEPT where a site is found in multiple CIFs with the same label, but different type. In this case, the
          returned lists of labels and types *should* work correctly when run through calcellipsoid.calcfromcif
    """
    
    log.debug('Checking ligand types and labels')
    
    # Iterate through all cifs, adding label:[type1, <type2>...] pairs to overall dict
    ligtyplbls = {}
    for c in cifs:
        typlbls = _alltyplbls(c, phase)      # Get labels and types from current cif
        for l in typlbls:
            if l in ligtyplbls.keys():      # Label already exists in overall dict - if the type is the same, we can ignore it
                if typlbls[l] in ligtyplbls[l]:
                    continue
                else:                       # Types are different: append type to label list
                    ligtyplbls[l].append(typlbls[l])
            else:                       # Label doesn't already exist; add
                ligtyplbls[l] = [typlbls[l]]
    
    # Get sets of all types and labels
    alltypes = set([ i for l in ligtyplbls for i in ligtyplbls[l]])
    alllbls = set( ligtyplbls.keys() )
    
    testtyp, omittyp, missingtyp = check_labels(ligtypes, alltypes)
    testlbl, omitlbl, missinglbl = check_labels(liglbls, alllbls)   

    # Get final lists of labels and types to test
    if len(testtyp) == 0 and len(testlbl) == 0:    # No ligands have been specified; use everything apart from exclusions
        log.warning("No valid ligand types/labels were given; using all types")
        finallbl = alllbls.copy()
        finaltyp = alltypes.copy()
    elif len(testtyp) == 0:         # Presume only labels are supplied
        finallbl = alllbls.copy()
        finaltyp = set()
    elif len(testlbl) == 0:         # Presume only types are supplied
        finallbl = set()
        finaltyp = set(testtyp)
    else:
        finallbl = set(testlbl)
        finaltyp = set(testtyp)
        
    # Remove values corresponding to omit expressions
    if len(omittyp) > 0:                        # Omit types first, as more general
        toomit = []
        for o in omittyp:                       # Iterate over omit types, appending corresponding labels to list
            for l in finallbl:                  # Iterate over labels selected
                if ligtyplbls[l] == [o]:        # Omit label ONLY if it has the single type (keep otherwise) ; further basic filtering is performed by calcfromcif
                    toomit.append(l)
        finallbl.difference_update(toomit)       # finallbl should now contain a list of site labels to test
        finaltyp.difference_update(omittyp)
    
    # Need to remove labels supplied by omit, as well as types no longer required (i.e. if label omit removes all atoms of type XX)
    if len(omitlbl) > 0:                        # Omit sites by label
        finallbl.difference_update(omitlbl)
        
        # Work out if any types need to be removed
        typfromlbl = set([ i for l in finallbl for i in ligtyplbls[l]])
        toomit = []
        for o in omitlbl:
            for t in ligtyplbls[o]:
                if t not in typfromlbl and t not in testtyp:        # Type does not occur from supplied labels, nor from supplied types - remove type
                    toomit.append(t)
                    
        finaltyp.difference_update(toomit)
        
    
    if len(missingtyp) > 0:
        log.warning("Ligand(s) %s are not valid types for any CIF files; they will be skipped", str(", ".join(missingtyp)))
    if len(missinglbl) > 0:
        log.warning("Ligand(s) %s are not valid labels for any CIF files; they will be skipped", str(", ".join(missinglbl)))
    
    return list(finallbl), list(finaltyp)
    
    
def run_parallel(cifs, testcen, radius=3.0, ligtypes=[], lignames=[], maxcycles=None, tolerance=1e-6, procs=None, phase=None):
    """ Run ellipsoid computation in parallel, by CIF file """

    import threading
    ## Add queue to deal with passing logging messages
    queue = multiprocessing.Queue(-1)
    
    # Run listener as thread so that logs on queue can be passed back to parent
    # (when run as separate process, logs from subprocesses are lost if not handled immediately)
    lp = threading.Thread(target=listener_process, args=(queue, listener_empty_config,))
    lp.start()
    
    # Start multiprocessing Pool, calling worker_configure on startup to send worker logging to queue
    log.debug('Starting multiprocess pool')
    if procs is not None:
        pool = multiprocessing.Pool(procs, worker_configure, [queue])
    else:
        pool = multiprocessing.Pool(None, worker_configure, [queue])
    # Construct input for each cif file
    vals = [ (i, testcen, radius, ligtypes, lignames, maxcycles, tolerance, phase,) for i in cifs ]

    try:
        err = False
        log.warning('Processing all cif files...')
        log.info('Using options:')
        for a in ['cifs', 'testcen', 'radius', 'ligtypes', 'lignames', 'maxcycles', 'tolerance', 'procs']:
            log.info('{0:20s} : {1}'.format(a, vars()[a]))

        results = pool.map(_wrapper, vals)
        pool.close()
    except KeyboardInterrupt:
        err = True
        log.critical('got ^C while processing files, terminating all processes')
        pool.terminate()
        log.critical('Terminated successfully')
        raise
    except Exception as e:
        err = True
        log.critical('got exception: %r, terminating all processes' % (e,))
        pool.terminate()
        log.critical('Terminated successfully')
        raise
    except:
        err = True
        raise
    finally:
        if err:
            # Force pool to end if not already
            try:
                pool.terminate()
            except:
                pass
        else:
            pool.join()
        

        log.debug('Closed multiprocessing Pool')

        queue.put_nowait(None)
        #listener.join()
        lp.join()
            
    log.warning('Finished processing all CIFs')
    
    # Assign multiprocess values to phase dict (should be in correct order when using pool.map)
    phases = {}
    for i, file in enumerate(cifs):
        if isinstance(results[i], Exception):
            log.error("Error reading file %s - skipped", file)
        else:
            phases[file] = results[i]
    
    return phases
            
def run_serial(cifs, testcen, radius=3.0, ligtypes=[], lignames=[], maxcycles=None, tolerance=1e-6, phase=None):
    log.warning('Processing all cif files...')
    log.info('Using options:')
    for a in ['cifs', 'testcen', 'radius', 'ligtypes', 'lignames', 'maxcycles', 'tolerance', 'phase']:
        log.info('{0:20s} : {1}'.format(a, vars()[a]))
        
    phases = {}
    for i, CIF in enumerate(cifs):
        #log.debug("Starting file %s",CIF)
        try:
            phases[CIF] = calcellipsoid.calcfromcif(CIF, testcen, radius, allligtypes=ligtypes, alllignames=lignames, maxcycles = maxcycles, tolerance=tolerance, phase=phase)
        except KeyError:
            log.critical("\nValid atom labels are:\n\n %s", ", ".join(_alllabels(CIF, phase)))
            raise
        except KeyboardInterrupt:
            log.warning("Terminated successfully")
            sys.exit()
        except RuntimeError:
            raise
        except IOError:
            raise
    log.warning('Finished processing all CIFs') 
    
    return phases
    
def plot_all(phases):
    plots = {}
    for CIF in phases.keys():
        plots[CIF] = {}    
        for cen in getattr(phases[CIF], 'polyhedra'):
            colours = getattr(phases[CIF], cen+"_poly").pointcolours()
            plots[CIF][cen] = getattr(phases[CIF], cen+"_poly").ellipsoid.plotsummary(title=CIF+': '+cen, pointcolor=colours)
            
    return plots
            
def main(cifs, centres, **kwargs):
    """ Process all supplied cif files using options supplied as kwargs (or defaults).
    
    Returns
        phases : Dict
            Dictionary of Crystal objects (containing ellipsoid results), keyed by CIF name.
        plots : dict or dicts, optional
            Dictionary of summary plots (keyed by CIF name) containing Dictionary
            of plots (keyed by ellipsoid centre)
    """

    multiprocessing.freeze_support()
    
    defaults = {}
    defaults['outfile'] = None
    defaults['radius'] = 3.0
    defaults['ligtypes'] = []
    defaults['lignames'] = []
    defaults['tolerance'] = 1e-6
    defaults['maxcycles'] = None
    defaults['nosave'] = False
    defaults['writeall'] = False
    defaults['printlabels'] = False
    defaults['nothread'] = False
    defaults['procs'] = None
    defaults['noplot'] = False
    defaults['pickle'] = False
    defaults['writelog'] = False
    defaults['phase'] = None
    
    # Sort out all arguments using defaults where necessary
    args = {}
    for a in defaults:
        args[a] = kwargs.get(a, defaults[a])
        
    #print args['phase']    
    cifs = [os.path.normpath(i) for i in cifs]   
    
    if args['writelog']:
        # Set up handler for all debug output (adding to root handler)
        root = logging.getLogger()
        debug = logging.FileHandler('./debug.log', mode='w')
        debugform = logging.Formatter('%(name)-40s %(funcName)-20s %(processName)-13s %(levelname)-8s %(message)s')
        debug.setFormatter(debugform)
        root.addHandler(debug)
        root.setLevel(logging.DEBUG)
        log.debug('Turned on file logging')
    
    # Print labels if requested, then exit
    if args['printlabels']:
        log.critical("Valid atom labels are:\n\n")
        for CIF in cifs:
            log.critical("{0:<40}:  {1}".format(CIF, ", ".join(_alllabels(CIF, args['phase']))))
        return
    elif centres is None or len(centres) == 0:
        raise ValueError("At least one polyhedron centre is required.")
        
    # Check input and output files match
    if args['outfile'] is None:
        args['outfile'] = [ os.path.splitext(i)[0]+'.txt' for i in cifs ]
    else:
        if len(args['outfile']) != len(cifs):
            raise ValueError("Number of output files does not match input files")
     
    # Check centre labels, and then perform calculation
    try:
        testcen = check_centres(cifs, centres, args['phase'])
        if testcen is None:
            return (None, None)
     
        testliglbl, testligtyp = check_ligands(cifs, args['ligtypes'], args['lignames'], args['phase'])
        if len(testliglbl) == 0 and len(testligtyp) == 0:
            log.critical('No suitable ligands have been defined - stopping')
            return (None, None)
        
     
        phases = {}
    
        if len(cifs) > 1 and not args['nothread'] and args['procs'] != 1:
            log.debug('Running calculation in parallel')
            phases = run_parallel(cifs,
                                testcen,
                                radius=args['radius'],
                                #ligtypes=args['ligtypes'],
                                #lignames=args['lignames'],
                                ligtypes=testligtyp,
                                lignames=testliglbl,
                                maxcycles=args['maxcycles'],
                                tolerance=args['tolerance'],
                                procs=args['procs'],
                                phase = args['phase'])
            log.debug('Finished parallel calculation')
        
        else:
            log.debug('Running calculation in serial')
            phases = run_serial(cifs,
                                testcen,
                                radius=args['radius'],
                                #ligtypes=args['ligtypes'],
                                #lignames=args['lignames'],
                                ligtypes=testligtyp,
                                lignames=testliglbl,
                                maxcycles=args['maxcycles'],
                                tolerance=args['tolerance'],
                                phase = args['phase'])
            log.debug('Finished serial calculation')
    except:
        log.exception("Ellipsoid calculation aborted abnormally: see traceback for details")
        raise

    if not args['nosave']:
        for i, CIF in enumerate(cifs):
            writeproperties.writeall(args['outfile'][i], phases[CIF], verbosity=3, overwrite=args['writeall'])
    
    if not args['noplot']:
        plots = plot_all(phases)
    else:
        plots = {}
                
    if args['pickle']:
        import pickle
        pickle.dump(phases, open("ellipsoid_dat.pkl", "w"))
        
    log.warning("Processing completed successfully")    

    if args['writelog']:
        debug.close()
        root.removeHandler(debug)
        
    return phases, plots
        
        
        
if __name__ == "__main__":
    raise EnvironmentError("Please use CIFellipsoid.py script when running on the command line.")
        
