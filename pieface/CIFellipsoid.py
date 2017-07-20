#!/usr/bin/env python

"""
Calculate minimum-bounding-ellipsoid for polyhedra, based on a list of Cif files.
"""

import multiprocessing
from pieface import __version__
from json import loads
import sys
from urllib2 import urlopen

        
def _alllabels(CIF, phase=0):
    """ Return all allowed labels in CIF file. """
    from pieface.readcoords import readcif
    cell, atomcoords, atomtypes, spacegp, symmops, symmid = readcif(CIF, phase)
    return atomcoords.keys()

def _query(question, default="yes", output=None):
    """Ask a yes/no question via raw_input() and return their answer. """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'".format(default))

    while True:
        output.critical(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            output.critical("Please respond with 'yes' or 'no' (or 'y' or 'n').\n")
            

def check_update(log=None):
    """ Check if a newer version of PIEFACE has been released """
    
    try:
        u = urlopen('https://api.github.com/repos/jcumby/PIEFACE/releases/latest').read()
        ujson = loads(u)
        
    except:
        # Problem reading url (perhaps no internet)?
        return
    
    newversion = ujson['tag_name'][1:].split('.')
    currversion = __version__.split('.')
    assert len(newversion) == len(currversion)
    
    for i, num in enumerate(currversion):
        if int(newversion[i]) > int(num):
            if log is None:
                print "A newer version of PIEFACE is now available ({0})".format(".".join(newversion))
                if hasattr(sys, 'frozen'):
                    print 'The newer version can be downloaded from https://github.com/jcumby/PIEFACE/releases/latest'
                else:
                    print 'Consider upgrading from https://github.com/jcumby/PIEFACE or PyPI'
            else:
                log.warning("A newer version of PIEFACE is now available ({0})".format(".".join(newversion)))
                if hasattr(sys, 'frozen'):
                    log.warning('The newer version can be downloaded from https://github.com/jcumby/PIEFACE/releases/latest')
                else:
                    log.warning('Consider upgrading from https://github.com/jcumby/PIEFACE or PyPI')

    return
        

def main():

    import sys
    if sys.platform.startswith('win'):
        # # Hack for multiprocessing.freeze_support() to work from a
        # # setuptools-generated entry point.
        # if __name__ != "__main__":
            # sys.modules["__main__"] = sys.modules[__name__]
        multiprocessing.freeze_support()

    from pieface import multiCIF
    import argparse
    import sys
    import logging
    
    class VersionAction(argparse.Action):
        def __init__(self,
                     option_strings,
                     version=None,
                     nargs=None,
                     **kwargs):
            if nargs is not None:
                raise ValueError("nargs not allowed")
            super(VersionAction, self).__init__(option_strings, nargs=0, **kwargs)
            self.version=version
            
        def __call__(self, parser, namespace, values, option_string=None):
            version = self.version
            print "PIEFACE {0}".format(__version__)
            check_update()
            sys.exit()
    
    parser = argparse.ArgumentParser(description="Compute ellipsoid properties from CIF file(s).")
    parser.add_argument("cifs",
                        type=str,
                        action="store",
                        nargs="+",
                        help="Name of Cif files to import")
    parser.add_argument("-o","--output",
                        action="store",
                        type=str,
                        dest="outfile",
                        default=None,
                        nargs="*",
                        help="Name of output files")
    parser.add_argument("-m", "--metal",
                        action="store",
                        type=str,
                        dest="centres",
                        required=False,     # Handle manually later
                        nargs="+",
                        help="Symbol of polyhedron centres to analyse. #NN will omit from search, and regular expressions are allowed")
    parser.add_argument("-r", "--radius",
                        action="store",
                        type=float,
                        dest="radius",
                        default=3.0,
                        help="Max distance for metal-ligand bond in Angstrom, default 3.0")
    parser.add_argument("-l", "--ligandtypes",
                        action="store",
                        type=str,
                        dest="ligtypes",
                        default=[],
                        nargs="*",
                        help="Types of atom to be considered ligand (default all)")
    parser.add_argument("-n", "--ligandnames",
                        action="store",
                        type=str,
                        dest="lignames",
                        default=[],
                        nargs="*",
                        help="Labels of atom to be considered as ligands (default all allowed by type)")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-t","--tolerance",
                        action="store",
                        type=float,
                        dest="tolerance",
                        default=1e-6,
                        help="Maximum tolerance for fitting ellipsoid (default 1e-6)")
    group.add_argument("--maxcycles",
                        action="store",
                        type=int,
                        default=None,
                        help="Maxmimum number of iterations for ellipsoid fitting (default infinite)")
    parser.add_argument("-b", "--block",
                         action="store",
                         type=str,
                         dest="phase",
                         default=None,
                         help="Name of datablock to read from CIF (default None reads the first alphabetically)")
    parser.add_argument("-N",
                         action="store_true",
                         dest="nosave",
                         help="Don't save calculated properties to file")
    parser.add_argument("-W","--overwriteall",
                        action="store_true",
                        dest="writeall",
                        help="Force all necessary output files to be overwritten")
    parser.add_argument("-P", "--PrintLabels",
                         action="store_true",
                         dest="printlabels",
                         help="Print valid atom labels from CIF and exit")
    parser.add_argument("-U", "--Unthreaded",
                         action = "store_true",
                         dest = "nothread",
                         help="Turn off parallel processing of CIF files")
    parser.add_argument("--procs",
                         action="store",
                         default=None,
                         type=int,
                         nargs= "?",
                         help="Number of processors to use (default all")
    parser.add_argument("--noplot",
                         action="store_true",
                         dest="noplot",
                         help="Turn of plotting of ellipsoid(s) with summary")
    parser.add_argument("--writelog",
                         action="store_true",
                         dest = "writelog",
                         help = "Write processing log to `debug.log`")
    parser.add_argument("--pickle",
                         action="store_true",
                         dest="pickle",
                         help=argparse.SUPPRESS)        # Secret option to save phase dict to "ellipsoid_dat.pkl"
    parser.add_argument("-V", "--version", 
                        action=VersionAction,
                        version="PIEFACE {0}".format(__version__),
                        help="Print PIEFACE information and check for updates before exit")
                         
    try:
        args = parser.parse_args()
    except:
        sys.exit()
        
    log = logging.getLogger()
    h = logging.StreamHandler()
    h.setLevel(logging.WARNING)
    log.addHandler(h)
    
    cifs = []
    for c in args.cifs:
        if '*' in c:
            # Treat as regular expression
            import glob
            cifs = cifs + glob.glob(c)
        else:
            cifs.append(c) 
            
    try:
        if args.printlabels:
            log.warning("\nValid atom labels are:\n")
            for CIF in cifs:
                log.critical("{0:<40}:  {1}".format(CIF, ", ".join(_alllabels(CIF))))
            raise
        elif args.centres is None:
            # Behave like argparse error
            parser.print_usage()
            log.critical("CIFellipsoid.py: error: argument -m/--metal is required")
            raise

        if args.nosave:
            if not _query("Option `-N` will not save any data; do you want to continue?", default="no", output=log):
                raise
                
        argdict = vars(args)
        
        centres = argdict.pop('centres')
        argdict.pop('cifs')
        
        try:
            phases, plots = multiCIF.main(cifs, centres, **argdict)
        except:
            pass
    except:
        pass
    finally:
        log.removeHandler(h)
        sys.exit()            
            
if __name__ == "__main__":
    import sys
    if sys.platform.startswith('win'):
        # Hack for multiprocessing.freeze_support() to work from a
        # setuptools-generated entry point.
        # if __name__ != "__main__":
            # sys.modules["__main__"] = sys.modules[__name__]
        multiprocessing.freeze_support()
    main()


 

        

