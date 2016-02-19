"""
Module for processing one or more CIF files using supplied options

To run from the command line, call the CIFellipsoid.py script.
    
"""


import logging, sys, os
import multiprocessing
from distellipsoid import writeproperties, calcellipsoid
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
    ## Can be used to turn of passing of CTRL-C to sub-processes, but then 
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
    from distellipsoid import calcellipsoid
    try:
        return calcellipsoid.calcfromcif(args[0], args[1], args[2], allligtypes=args[3], alllignames=args[4], maxcycles=args[5], tolerance=args[6])
    except IOError as e:    # Except IOErrors so that missing files are handled sensibly...
        return e
    except KeyboardInterrupt:
        raise KeyboardInterruptError()
        
def _alllabels(CIF):
    """ Return all allowed labels in CIF file. """
    from distellipsoid.readcoords import readcif
    cell, atomcoords, atomtypes, spacegp, symmops, symmid = readcif(CIF)
    return atomcoords.keys()
    
 
def check_centres(cifs, centres):
    """ Determine which centres to use based on CIF contents and user-supplied arguments."""
    # Work out what centres to include
    log.debug('Checking centre labels')
    allcentres = set([ i for c in cifs for i in _alllabels(c) ])
    testcen = set()
    omitcen = set()
    for c in centres:
        if any( [i in c for i in ['*','$','^','.','+','?','{','}','|','[',']','\\']] ):  # Treat as regex (approximately)
            if c[0] == '#':     # omit centres
                found = False
                for a in allcentres:
                    if re.search(c[1:], a):     # Regex matches
                        omitcen.add(a)
                        found = True
                if not found:
                    log.warning("Regular expression %s did not match any centre labels; skipping", c[1:])
            else:           # Find centres based on regex       
                found = False
                for a in allcentres:
                    if re.search(c, a):     # Regex matches
                        testcen.add(a)
                        found = True
                if not found:
                    log.warning("Regular expression %s did not match any centre labels; skipping", c)
        elif c[0] == '#':      # Omit centre with # prepending name
            omitcen.add(c[1:])
            continue
        else:
            testcen.add(c)
    if len(testcen) == 0:       # Empty list was passed apart from exclusions: add all atoms apart from those
        testcen = allcentres.copy()
        testcen.difference_update(omitcen)
        
    if not set(testcen).issubset(allcentres):
        log.critical("Label(s) %s are not present in any of the CIF files - stopping", str(" ".join([str(i) for i in set(testcen).difference(allcentres)])))
        log.critical("Valid atom labels are:\n")
        for CIF in cifs:
            #log.warning("{0:<40}:  {1}".format(CIF, ", ".join(_alllabels(CIF))))
            log.critical("%-40s:  %s", CIF, ", ".join(_alllabels(CIF)))
        #raise ValueError
        return
 
    return testcen
    
def run_parallel(cifs, testcen, radius=3.0, ligtypes=[], lignames=[], maxcycles=None, tolerance=1e-6, procs=None):
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
    vals = [ (i, testcen, radius, ligtypes, lignames, maxcycles, tolerance,) for i in cifs ]

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
    except Exception, e:
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
            
def run_serial(cifs, testcen, radius=3.0, ligtypes=[], lignames=[], maxcycles=None, tolerance=1e-6):
    log.warning('Processing all cif files...')
    log.debug('Using options:')
    for a in ['cifs', 'testcen', 'radius', 'ligtypes', 'lignames', 'maxcycles', 'tolerance']:
        log.debug('{0:20s} : {1}'.format(a, vars()[a]))
        
    phases = {}
    for i, CIF in enumerate(cifs):
        #log.debug("Starting file %s",CIF)
        try:
            phases[CIF] = calcellipsoid.calcfromcif(CIF, testcen, radius, allligtypes=ligtypes, alllignames=lignames, maxcycles = maxcycles, tolerance=tolerance)
        except KeyError:
            log.critical("\nValid atom labels are:\n\n %s", ", ".join(_alllabels(CIF)))
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
    -------
    phases : Dict
            Dictionary of Crystal objects (containing ellipsoid results), keyed by CIF name.
    plots : dict or dicts, optional
            Dictionary of summary plots (keyed by CIF name) containing Dictionary
            of plots (keyed by ellipsoid centre)
    """

    
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
    
    # Sort out all arguments using defaults where necessary
    args = {}
    for a in defaults:
        args[a] = kwargs.get(a, defaults[a])
        
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
            log.critical("{0:<40}:  {1}".format(CIF, ", ".join(_alllabels(CIF))))
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
        testcen = check_centres(cifs, centres)
        if testcen is None:
            return (None, None)
     
        phases = {}
    
        if len(cifs) > 1 and not args['nothread'] and args['procs'] != 1:
            log.debug('Running calculation in parallel')
            phases = run_parallel(cifs,
                                testcen,
                                radius=args['radius'],
                                ligtypes=args['ligtypes'],
                                lignames=args['lignames'],
                                maxcycles=args['maxcycles'],
                                tolerance=args['tolerance'],
                                procs=args['procs'])
            log.debug('Finished parallel calculation')
        
        else:
            log.debug('Running calculation in serial')
            phases = run_serial(cifs,
                                testcen,
                                radius=args['radius'],
                                ligtypes=args['ligtypes'],
                                lignames=args['lignames'],
                                maxcycles=args['maxcycles'],
                                tolerance=args['tolerance'])
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
        