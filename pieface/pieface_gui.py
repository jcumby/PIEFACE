#!/usr/bin/python

""" Graphical interface to multiCIF, offering a GUI equivalent of CIFellipsoid.py. """

import Tkinter as tk
import tkMessageBox
import tkFileDialog
import ttk

import os, sys
import pieface
from pieface import multiCIF
from pieface.calcellipsoid import makeDataFrame
import traceback
import threading
import logging
import multiprocessing
import Queue

import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.backend_bases import key_press_handler
from mpl_toolkits.mplot3d import Axes3D

import pandas as pd
import urllib2
import json
import webbrowser

import pkg_resources

log = logging.getLogger()
#log.setLevel(logging.debug)

# Try to get ICON location based on multiCIF location
#multiCIFloc = os.path.dirname( multiCIF.__file__ )
#iconloc = os.path.abspath(os.path.join( multiCIFloc, '..', 'docs', 'images', 'pieface.ico'))
if os.name == 'nt':
    iconloc = pkg_resources.resource_filename('pieface', 'data/pieface.ico')
elif os.name == 'posix':
    iconloc = '@' + pkg_resources.resource_filename('pieface', 'data/pieface.xbm')

class MainWindow:
    def __init__(self, parent):
        """ Initialise main window. """
        self.parent = parent
        self.parent.title("PIEFACE Input GUI")
        
        # Make all errors propagated to MainWindow.parent call custom exception routine
        parent.report_callback_exception = self.report_callback_exception
        
        self.filenames = []
        
        self.nbookmain = ttk.Notebook(self.parent)
        self.intab = ttk.Frame(self.nbookmain)
        self.logtab = ttk.Frame(self.nbookmain)
        self.nbookmain.add(self.intab, text='Input', sticky='nesw')
        self.nbookmain.add(self.logtab, text='Output log', sticky='nesw', state=tk.NORMAL)
        
        self.log = LogDisplay(self.logtab)
        #self.log.__init__(self.logtab)
        self.log.pack(expand=1, fill=tk.BOTH)
        
        self.init_menu()
        
        self.init_gui(self.intab)
        
        self.nbookmain.pack(expand=1, fill=tk.BOTH)
        self.intab.columnconfigure(0, weight=1)
        self.intab.rowconfigure(0, weight=1)
        
        self.nbookmain.select(self.logtab)
        self.nbookmain.select(self.intab)
        
        self.find_updates(verbose=False)

    def report_callback_exception(self, *args):
        """ Modify exception behaviour to print to message box if not caught """
        a = traceback.format_exception(*args)
        msglst=["An unexpected error has occurred:\n",
                a[-1],
                a[-2],
                "More details can be found in the Output Log.\n",
                "Please report any bugs to james.cumby@ed.ac.uk, including a copy ",
                "of the output log and a description of how the error was produced."]
                
        #log.error(a)
        tkMessageBox.showerror("Error", "\n".join(msglst))
        #log.Error(args[0], args[1], args[2])

        
    def init_gui(self, parent):
        """ Initialise the GUI layout"""
        # Make frame to hold everything in window
        self.frame = ttk.Frame(parent)
        # Set grid expansion options in main frame
        self.frame.grid(sticky=(tk.N, tk.S, tk.E, tk.W))        # Main frame expands with window
        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=3)
        self.frame.rowconfigure(1, weight=1, minsize=30)
        self.frame.rowconfigure(3, weight=1, minsize = 30)

        self.parent = parent

        # File open button
        self.filebutton = ttk.Button(self.frame, text="Add File(s)", command = self.openfiles)
        self.filebutton.grid(row=0, column = 3, sticky=(tk.NE, tk.NW), padx=3)
        # Remove file button
        self.clearbutton = ttk.Button(self.frame, text="Remove File(s)", command = self.removefile, state='disabled')
        self.clearbutton.grid(row=1, column = 3, sticky=(tk.NE, tk.NW), padx=3)
    
        # Frame to hold file box and scrollbars
        self.fileframe = ttk.Frame(self.frame)
        self.fileframe.grid(row=0, column=0, columnspan = 2, rowspan = 4, sticky = (tk.N, tk.E, tk.S, tk.W))
        self.fileframe.columnconfigure(0, weight=1)
        #self.fileframe.columnconfigure(1, weight=1)
        self.fileframe.rowconfigure(0, weight=1)
        
        # List box (from Tkinter, not ttk) to hold list of file names
        self.filebox = tk.Listbox(self.fileframe, width=30, selectmode =tk.EXTENDED)
        # Scrollbars
        self.filevscroll = ttk.Scrollbar(self.fileframe, orient=tk.VERTICAL)
        self.filehscroll = ttk.Scrollbar(self.fileframe, orient=tk.HORIZONTAL)
        # Set up scrollbars and box to communicate
        self.filebox.config(yscrollcommand = self.filevscroll.set)
        self.filebox.config(xscrollcommand = self.filehscroll.set)
        self.filevscroll.config(command=self.filebox.yview)
        self.filehscroll.config(command=self.filebox.xview)
        
        # Place items on fileframe grid
        self.filevscroll.grid(column=1, sticky = (tk.N, tk.S, tk.E))
        self.filehscroll.grid(column=0, row=1, sticky = (tk.E, tk.S, tk.W))
        self.filebox.grid(column=0, row=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        
        textargs = {}
        textargs['rad'] = ['Bond radius (ang.)', 3.5]
        textargs['cent'] = ['Polyhedron Centres (space separated)', '']
        textargs['ligt'] = ['Ligand Types', '']
        textargs['lign'] = ['Ligand Labels', '']
        textargs['tol'] = ['Fit tolerance', 1e-6]
        textargs['procs'] = ['Number of processors', multiprocessing.cpu_count()]
        textord = ['cent','ligt','lign','rad','tol','procs']

        rownow = 4
        
        for option in textord:
            setattr(self, option+'lbl', ttk.Label(self.frame, text = textargs[option][0]))
            getattr(self, option+'lbl').grid(column = 0, row= rownow, sticky = tk.W)
            setattr(self, option+'ent', ttk.Entry(self.frame))
            getattr(self, option+'ent').grid(column = 1, row= rownow, sticky = (tk.W, tk.E))
            if textargs[option][1] != '':
                getattr(self, option+'ent').insert(0, textargs[option][1])
                
            rownow += 1
        
        tickargs = {}
        tickargs['para'] = ['Process in parallel', True]
        tickargs['svout'] = ['Save results to file(s)', True]
        #tickargs['noplot'] = ["Plot ellipsoids", True]
        
        for option in tickargs:
            setattr(self, option+'var', tk.IntVar())
            if tickargs[option][1]:
                getattr(self, option+'var').set(1)
            else:
                getattr(self, option+'var').set(0)
            setattr(self, option+'chk', ttk.Checkbutton(self.frame, text = tickargs[option][0], variable = getattr(self, option+'var'), command = lambda c=option: self.disable_check(c)  ))
            getattr(self, option+'chk').grid(column = 0, row= rownow, sticky = tk.W)
            rownow += 1

        # Add custom options button
        self.extravar = tk.IntVar()
        self.extravar.set(0)
        self.extrachk = ttk.Checkbutton(self.frame, text='Additional options (for advanced use)', variable=self.extravar, command = lambda c='extra': self.disable_check(c))
        self.extrachk.grid(column = 0, row=30, sticky=tk.W)
        self.extraent = ttk.Entry(self.frame, state='disabled')
        self.extraent.grid(column = 1, row=30, sticky=(tk.W, tk.E))
 
        # Quit button
        self.closeButton = ttk.Button(self.frame, text="Close", command=self._quit)
        self.closeButton.grid(row=40, column=3, padx=1, sticky=(tk.W, tk.E), pady=(10,1))            
 
        # Run button
        self.runButton = ttk.Button(self.frame, text="Calculate All", command=self.run)
        self.runButton.grid(row=40, column=1, padx=1, sticky=(tk.E), pady=(10,1))
        
        self.runButton.config(width = 20)

        
        # Results button
        self.resultsbutton = ttk.Button(self.frame, text="Plot Results", command = lambda: self.make_plot_win(self.filebox.curselection()), state='disabled')
        self.resultsbutton.grid(row=2, column = 3, sticky=(tk.NE,tk.NW), padx=3)
        
        # Summary button
        self.sumbutton = ttk.Button(self.frame, text="Results Summary", command = self.make_sum_win, state='disabled')
        self.sumbutton.grid(row=3, column = 3, sticky=(tk.NE,tk.NW), padx=3)

    def init_menu(self):
        """ Set up drop-down menus for the main window. """
        
        # Add menubar to parent window
        self.menubar = tk.Menu(self.parent)
        
        # Add menubar items and sub-options
        self.filemenu = tk.Menu(self.menubar, tearoff=0)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Exit", command=self._quit)
        
        self.helpmenu = tk.Menu(self.menubar, tearoff=0)
        self.helpmenu.add_command(label='View README', command=self.viewreadme)        
        self.helpmenu.add_command(label='View online manual', command=self.viewinternethelp)
        self.helpmenu.add_command(label='View PDF manual', command=self.viewhelp)
        self.helpmenu.add_separator()
        self.helpmenu.add_command(label='Check for updates', command=self.find_updates)
        self.helpmenu.add_command(label='About', command=self.about)
        
        self.menubar.add_cascade(label="File", menu=self.filemenu)
        self.menubar.add_cascade(label="Help", menu=self.helpmenu)
        
        # Simpler single option syntax
        #self.menubar.add_command(label='Quit', command=self._quit)
        #self.menubar.add_command(label='Help', command=self.viewhelp)
        
        self.parent.config(menu=self.menubar)
        
    def _quit(self):
        # Necessary to avoid problems with matplotlib on exit with Windows
        self.parent.quit()
        self.parent.destroy()
        
    def viewreadme(self):
        """ Open README file in default viewer """

        try:
            # Try to get README location based on multiCIF location
            README = pkg_resources.resource_filename('pieface_docs', 'README.pdf')
            #README = os.path.abspath(os.path.join( multiCIFloc, '..', 'README.pdf'))
            webbrowser.open(README)
        except:
            tkMessageBox.showerror("Error", "Cannot find README location")
            
    def viewhelp(self):
        """ Open help file in default viewer """

        try:
            # Try to get help file location based on multiCIF location
            PDFhelp = pkg_resources.resource_filename('pieface_docs', 'PIEFACE_manual.pdf')
            #PDFhelp = os.path.abspath(os.path.join( multiCIFloc, '..', 'docs', 'PIEFACE_manual.pdf'))
            webbrowser.open(PDFhelp)
        except:
            tkMessageBox.showerror("Error", "Cannot find help file location")
            
    def viewinternethelp(self):
        """ Open online documentation in default webbrowser"""

        webbrowser.open('http://pieface.readthedocs.io/')
    
    def openfiles(self):
        """ Open dialog for selecting CIF files"""
        options = {}
        options['initialdir'] = '{0}'.format(os.path.expanduser('~'))
        options['filetypes'] = [('all files', '.*'), ('CIF files', '.cif')]
        options['title'] = 'CIF files for processing'
        options['defaultextension'] = '.cif'
        filenames = tkFileDialog.askopenfilenames(parent=self.parent, **options)
        
        filelist = self.parent.tk.splitlist(filenames)
        
        for file in filelist:
            if os.path.normpath(file) not in self.filenames:
                self.filenames.append(os.path.normpath(file))
                self.filebox.insert(tk.END, os.path.basename(file) )
        if len(self.filenames) > 0:
            self.clearbutton.configure(state='normal')
        
    def removefile(self):
        """ Remove file from input list"""
        files = self.filebox.curselection()
        pos = 0

        for index in files:
            # Remove results corresponding to file (if present)
            if self.filenames[index - pos] in self.phases:
                self.phases.pop(self.filenames[index - pos])
            
            self.filebox.delete(index - pos)
            self.filenames.pop(index - pos)
            pos += 1
        if len(self.filenames) == 0:
            self.clearbutton.configure(state='disabled')
            self.resultsbutton.configure(state='disabled')
            self.sumbutton.configure(state='disabled')
            
    def check_update(self):
        """ Check if a newer version of PIEFACE has been released """
        
        try:
            u = urllib2.urlopen('https://api.github.com/repos/jcumby/PIEFACE/releases/latest').read()
            ujson = json.loads(u)
            
        except:
            # Problem reading url (perhaps no internet)?
            tkMessageBox.showerror("Update Error", "Failed to check for updates")
            return False
        
        newversion = ujson['tag_name'][1:].split('.')
        #currversion = pkg_resources.get_distribution('pieface').version.split('.')
        currversion = pieface.__version__.split('.')
        assert len(newversion) == len(currversion)
        
        
        for i, num in enumerate(currversion):
            if int(newversion[i]) > int(num):
                return True
        return False
        
    def find_updates(self, verbose=True):
        """ Run check_update and as user whether to update. """
        if self.check_update():
            if tkMessageBox.askyesno('Download update', 'An updated version of PIEFACE exists, do you want to download it?'):
                webbrowser.open('https://github.com/jcumby/PIEFACE/releases/latest')
        else:
            if verbose:
                tkMessageBox.showinfo('Update','PIEFACE is up to date')
            
    def about(self):
        """ Return information about pieface """
        tkMessageBox.showinfo('About', 'PIEFACE version {0}\n\n(c) James Cumby 2017\n\njames.cumby@ed.ac.uk'.format(pieface.__version__))
        
    def disable_check(self, chkbutn):
        """ Disable entry boxes if check button is ticked"""
        if chkbutn == "para":
            if self.paravar.get() == 0:
                self.procsent.configure(state = 'disabled')
            else:
                self.procsent.configure(state = 'normal')
        if chkbutn == "extra":
            if self.extravar.get() == 0:
                self.extraent.configure(state = 'disabled')
            else:
                self.extraent.configure(state = 'normal')
                
    def hide(self):
        self.parent.withdraw()
    def show(self):
        self.parent.update()
        self.parent.deiconify()

    def check_completed(self):
        """ Check if calculation has finished, and update GUI as necessary. """
        if hasattr(self.calcthread, 'isAlive'):
            # Calculation running using threading (also has is_alive() method...)
            if self.calcthread.isAlive():
                self.parent.after(50, self.check_completed)
            else:
                self.prog.stop()
                self.prog.grab_release()
                self.runButton.config(state='enabled')
                self.parent.config(cursor="")
                try:
                    #self.phases, self.sumplots = self.resQ.get()
                    queueout = self.resQ.get()
                except:
                    raise

                if queueout is None:
                    # Assume that multiCIF has returned None (aborted calculation]
                    self.phases = None
                    self.sumplots = None
                elif len(queueout) == 2:
                    # Normal operation
                    self.phases, self.sumplots = queueout
                elif len(queueout) == 3:
                    # multiCIF raised an error
                    #self.report_callback_exception(*queueout)
                    raise queueout[0], queueout[1], queueout[2]
                    
                # Manually write to logger window (log.info does not work here...)
                self.log.console.config(state = tk.NORMAL)
                self.log.console.insert(tk.END, '*************************\n')
                self.log.console.config(state=tk.DISABLED)
                self.log.console.see(tk.END)
                if self.phases is None:
                    pass
                elif len(self.phases) > 0:
                    self.resultsbutton.config(state = 'normal')
                    self.sumbutton.config(state='normal')
                self.parent.update()          
        
        
        elif hasattr(self.calcthread, 'is_alive'):                
            # Calculation is being run using multiprocessing
            if self.calcthread.is_alive():
                self.parent.after(100, self.check_completed)
            else:
                multiCIF_stop(self.calcthread, self.listener, self.queue)
                self.prog.stop()
                self.prog.grab_release()
                self.runButton.config(state='enabled')
                self.parent.config(cursor="")

                #log.info('************************************')
                self.parent.update()
          
    
    def run(self):
        """ Run pieface calculation using multiCIF (through a parallel thread)."""
        if len(self.filenames) == 0:
            tkMessageBox.showerror('Error','No files have been selected.')
            return
        
        if len(self.filebox.curselection()) > 0:
            # Some files are currently selected: check whether to use them or all files
            if tkMessageBox.askyesno("File Selection", "Only calculate for selected files?"):
                procfiles = [self.filenames[i] for i in self.filebox.curselection()]
            else:
                procfiles = self.filenames
        else:
            procfiles = self.filenames
        
        for file in procfiles:
            if not os.path.isfile(file):
                tkMessageBox.showerror('Error', 'File {0} is not a valid file'.format(file))
                return
                
        # Check if any advanced options are passed
        if self.extravar.get():
            extravals = dict( [ i.split('=') for i in self.extraent.get().split()] )
        else:
            extravals = {}
        # Set up variables    
        vals = dict(outfile = None,
            radius = float(self.radent.get()),
            ligtypes = list(self.ligtent.get().split()),
            lignames = list(self.lignent.get().split()),
            tolerance = float(self.tolent.get()),
            maxcycles = int(extravals.get('maxcycles', 0)),
            nosave = not bool(self.svoutvar.get()),
            writeall = True,    # Overwrite all files by default
            printlabels = bool(extravals.get('printlabels', False)),
            nothread = not bool(self.paravar.get()),
            ptocs = int(self.procsent.get()),
            noplot = True,
            pickle = bool(extravals.get('pickle', False)),
            writelog = bool(extravals.get('writelog', False))
            )
        # Handle phaseblocks using advanced options...
        if 'b' in extravals.keys():
            vals['phase'] = extravals.get('b',None)
        elif 'block' in extravals.keys():
            vals['phase'] = extravals.get('block', None)
        elif 'phase' in extravals.keys():
            vals['phase'] = extravals.get('phase',None)
        else:
            vals['phase'] = None

        if vals['maxcycles'] <= 0:
            vals['maxcycles'] = None
        try:

            
            
            # Run calculation in a new thread
            self.resQ = Queue.Queue()
            self.calcthread = threading.Thread(target=multiCIF_thread_wrapper,
                                          args = (self.resQ,
                                                  self,
                                                  procfiles,
                                                  list(self.centent.get().split()),
                                                  ),
                                                  kwargs = vals)
                                                  
            # Run calculation in a multiprocessing Process, starting a listener queue for logging beforehand
            #self.calcthread, self.listener, self.queue = multiCIF_start((self.filenames,list(self.centent.get().split()),), vals)
            
            #self.calcthread = threading.Thread(target=slow_func, args=(5,))
                                        
            self.calcthread.start()
            
            
            self.runButton.config(state='disabled')
            self.parent.config(cursor="watch")
            self.prog = ProgressWindow(self)
            self.prog.grab_set()
            self.prog.start()
            self.parent.after(50, self.check_completed)

            # multiCIF.main(self.filenames,
                          # list(self.centent.get().split()),
                          # outfile = None,
                          # ligtypes=list(self.ligtent.get().split()),
                          # lignames = list(self.lignent.get().split()),
                          # tolerance = float(self.tolent.get()),
                          # maxcycles = None,
                          # nosave = bool(self.svoutvar),
                          # writeall = False,
                          # printlabels = False,
                          # nothread = not bool(self.paravar),
                          # noplot = False,
                          # pickle = False,
                          # writelog = False,
                          # )
                          
        #  prog = self.start_progress(self.frame)
        #    prog.start()
        except Exception, e:
            print "Exception caught in run"
            #exc_type, exc_value, exc_traceback = sys.exc_info()
            #self.report_callback_exception(exc_type, exc_value, exc_traceback)
            raise
        finally:
            pass
            
    def make_plot_win(self, selected):
        """ Create Toplevel window with selected data plotted """
        if len(selected) == 0:
            tkMessageBox.showerror('Error','Please select files to plot results.')
            return
        for selection in selected:
            if self.filenames[selection] not in self.phases:
                tkMessageBox.showerror('Error','No results exist for {0}'.format(self.filebox.get(selection)))
                continue
            if len( self.phases[self.filenames[selection]].polyhedra ) == 0:
                tkMessageBox.showerror('Error','No valid polyhedra exist for {0}'.format(self.filebox.get(selection)))
            
            crystob = self.phases[self.filenames[selection]]
            
            self.plotwin = tk.Toplevel()
            self.plotwin.iconbitmap(iconloc)
            self.plotwin.title("PIEFACE Ellipsoid Plots")
            self.plotnb = ttk.Notebook(self.plotwin)
            
            tabs = {}
            figs = {}
            for poly in sorted(crystob.polyhedra):    #Iterate through all polyhedra in Crystal object
                tabs[poly] = ttk.Frame(self.plotnb)
                self.plotnb.add(tabs[poly], text=poly, sticky='nesw')

                figs[poly] = PlotWindow(tabs[poly])
                figs[poly].updateplot(getattr(crystob, poly+'_poly').ellipsoid, title=self.filebox.get(selection), pointcolor = getattr(crystob, poly+"_poly").pointcolours())
                figs[poly].pack(expand=1, fill=tk.BOTH)
                
            self.plotnb.pack(expand=1, fill=tk.BOTH)
            
    def make_sum_win(self):
        """ Create top level window with Pandas summary DataFrame """
        self.sumwin = tk.Toplevel()
        self.sumwin.iconbitmap(iconloc)
        self.sumwin.title("PIEFACE Results Summary")
        self.sumnb = SummaryWindow(self.sumwin, self.phases)
        self.sumnb.pack(expand=1, fill=tk.BOTH)

class ProgressWindow(tk.Toplevel):
    """ Create window with progress bar. """
    def __init__(self, parent=None):
        self.parent = parent
        tk.Toplevel.__init__(self)
        #self.win = tk.Toplevel(parent)
        self.iconbitmap(iconloc)
        self.title('Busy')
        self.resizable(False, False)
        self.message = ttk.Label(self, text='Please wait. This may take a long time.')
        self.message.grid(column = 0, row=0, sticky = tk.N, padx=5, pady=5)
        self.prog = ttk.Progressbar(self, mode = 'indeterminate', orient=tk.HORIZONTAL, maximum=30)
        self.prog.grid(column=0, row=1, sticky=(tk.E, tk.W), padx=5, pady=5)
        tip = ttk.Label(self, text='[Tip: Perhaps a good time for a coffee?]')
        tip.grid(column=0, row=2, sticky=tk.S, padx=5, pady=5)
        #self.cancel = ttk.Button(self, text='Cancel', command=self.cancel)
        #self.cancel.grid(column=0, row=2, pady=5)
    def start(self):
        self.prog.start()
    def stop(self):
        self.prog.stop()
        self.destroy()
    def cancel(self):
        multiCIF_stop(self.parent.calcthread, self.parent.listener, self.parent.queue)
        #self.stop()
        
class PlotWindow(tk.Frame):
    """ Class to hold matplotlib plots """
    def __init__(self, parent):
        self.parent = parent
        tk.Frame.__init__(self, self.parent)
        
        self.updateplot(None)
        
        self.canvas.get_tk_widget().pack(side='top', fill='both', expand=1)
        
        self.toolbar = NavigationToolbar2TkAgg(self.canvas, self.parent)
        self.toolbar.update()
        self.canvas._tkcanvas.pack(fill='both', expand=1)
        
    def updateplot(self, ellipsoid, title=None, **kwargs):
        if ellipsoid is None:
            self.figure = matplotlib.figure.Figure()
            self.canvas = FigureCanvasTkAgg(self.figure, master=self.parent)
            self.canvas.show()
        else:
            self.figure.clf()
            ellipsoid.plotsummary(figure=self.figure, title=title, pointcolor=kwargs.get('pointcolor', 'r'))
            #self.figure.canvas.draw()
            self.canvas.show()
            
class SummaryWindow(tk.Frame):
    """ Class to hold summary table for ellipsoids """
    def __init__(self, parent, phases):
        if phases is not None and len(phases) > 0:
        
            self.parent = parent
            self.dframe = makeDataFrame(phases)
            
            self.init_menu()
            
            tk.Frame.__init__(self, self.parent)
            self.nb = ttk.Notebook(self)
            
            self.columnconfigure(0, weight=1)
            self.rowconfigure(0, weight=1)
            
            self.tabs = {}
            self.tables = {}
            vscrolls = {}
            hscrolls = {}
            
            if len(phases) == 1:
                # One phase; only plot `all` tab
                self.tabs['all'] = ttk.Frame(self.nb)
                self.nb.add(self.tabs['all'], text='All data', sticky='nesw')
                self.tabs['all'].columnconfigure(0, weight=1)
                self.tabs['all'].rowconfigure(0, weight=1)
            
                self.tables['all'] = tk.Text(self.tabs['all'], wrap='none', width=150)
                vscrolls['all'] = ttk.Scrollbar(self.tabs['all'], orient=tk.VERTICAL)
                hscrolls['all'] = ttk.Scrollbar(self.tabs['all'], orient=tk.HORIZONTAL)
                self.tables['all'].config(xscrollcommand = hscrolls['all'].set)
                self.tables['all'].config(yscrollcommand = vscrolls['all'].set)
                vscrolls['all'].config(command = self.tables['all'].yview)
                hscrolls['all'].config(command = self.tables['all'].xview)
            
                self.tables['all'].grid(column=0,row=0, sticky=(tk.W, tk.N, tk.S, tk.E))
                vscrolls['all'].grid(column=1, row=0, sticky=(tk.E,tk.N,tk.S))
                hscrolls['all'].grid(column=0,row=1, sticky=(tk.E,tk.W,tk.S))
                self.sframe = self.dframe[['r1','r2','r3','meanrad','rad_sig','shapeparam','centredisp','coordination']]
                self.sframe = self.sframe.rename(columns = {'r1':'R1','r2':'R2','r3':'R3','meanrad':'<R>','rad_sig':'sigma(R)','shapeparam':'S','centredisp':'Centre Displacement','coordination':'Coordination'})
                selection = ['R1','R2','R3','<R>','sigma(R)','S','Centre Displacement','Coordination']
            
                self.tables['all'].insert(tk.END, self.sframe[selection].to_string())
            else:
                self.tabs['all'] = ttk.Frame(self.nb)
                self.nb.add(self.tabs['all'], text='All data', sticky='nesw')
                self.tabs['all'].columnconfigure(0, weight=1)
                self.tabs['all'].rowconfigure(0, weight=1)
            
                self.tables['all'] = tk.Text(self.tabs['all'], wrap='none', width=150)
                vscrolls['all'] = ttk.Scrollbar(self.tabs['all'], orient=tk.VERTICAL)
                hscrolls['all'] = ttk.Scrollbar(self.tabs['all'], orient=tk.HORIZONTAL)
                self.tables['all'].config(xscrollcommand = hscrolls['all'].set)
                self.tables['all'].config(yscrollcommand = vscrolls['all'].set)
                vscrolls['all'].config(command = self.tables['all'].yview)
                hscrolls['all'].config(command = self.tables['all'].xview)
            
                self.tables['all'].grid(column=0,row=0, sticky=(tk.W, tk.N, tk.S, tk.E))
                vscrolls['all'].grid(column=1, row=0, sticky=(tk.E,tk.N,tk.S))
                hscrolls['all'].grid(column=0,row=1, sticky=(tk.E,tk.W,tk.S))
                self.sframe = self.dframe.loc[:, (slice(None),['r1','r2','r3','meanrad','rad_sig','shapeparam','centredisp','coordination']) ]
                self.sframe = self.sframe.rename(columns = {'r1':'R1','r2':'R2','r3':'R3','meanrad':'<R>','rad_sig':'sigma(R)','shapeparam':'S', 'centredisp':'Centre Displacement','coordination':'Coordination'})
                self.sframe.index = self.sframe.index.map(os.path.basename)
                # Simple way to ensure order is correct on output
                selection = pd.MultiIndex.from_product([self.sframe.columns.get_level_values(level=0).unique(), ['R1','R2','R3','<R>','sigma(R)','S', 'Centre Displacement','Coordination']])
                self.tables['all'].insert(tk.END, self.sframe[selection].to_string())
                
                for site in sorted(list(set(self.dframe.columns.get_level_values(level=0)))):
                    self.tabs[site] = ttk.Frame(self.nb)
                    self.nb.add(self.tabs[site], text=site, sticky='nesw')
                    self.tabs[site].columnconfigure(0, weight=1)
                    self.tabs[site].rowconfigure(0, weight=1)
                
                    self.tables[site] = tk.Text(self.tabs[site], wrap='none', width=150)
                    vscrolls[site] = ttk.Scrollbar(self.tabs[site], orient=tk.VERTICAL)
                    hscrolls[site] = ttk.Scrollbar(self.tabs[site], orient=tk.HORIZONTAL)
                    self.tables[site].config(xscrollcommand = hscrolls[site].set)
                    self.tables[site].config(yscrollcommand = vscrolls[site].set)
                    vscrolls[site].config(command = self.tables[site].yview)
                    hscrolls[site].config(command = self.tables[site].xview)
                
                    self.tables[site].grid(column=0,row=0, sticky=(tk.W, tk.N, tk.S, tk.E))
                    vscrolls[site].grid(column=1, row=0, sticky=(tk.E,tk.N,tk.S))
                    hscrolls[site].grid(column=0,row=1, sticky=(tk.E,tk.W,tk.S))
                    sframe = self.dframe.loc[:, (slice(site),['r1','r2','r3','meanrad','rad_sig','shapeparam','centredisp','coordination']) ][site]
                    sframe.index = sframe.index.map(os.path.basename)
                    sframe.rename(columns = {'r1':'R1','r2':'R2','r3':'R3','meanrad':'<R>','rad_sig':'sigma(R)','shapeparam':'S','centredisp':'Centre Displacement','coordination':'Coordination'}, inplace=True)
                    selection = ['R1','R2','R3','<R>','sigma(R)','S','Centre Displacement','Coordination']
                    
                    self.tables[site].insert(tk.END, sframe[selection].to_string())
            
            self.nb.grid(row=0, column=0, sticky=(tk.N, tk.E, tk.S, tk.W))
            self.nb.columnconfigure(0, weight=1)
            self.nb.rowconfigure(0, weight=1)

    def init_menu(self):
        """ Set up drop-down menus for the main window. """
        
        # Add menubar to parent window
        self.menubar = tk.Menu(self.parent)
        
        # Add menubar items and sub-options
        self.filemenu = tk.Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label='Save As...', command=self.savedata)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Close", command=self.parent.destroy)
        
        self.menubar.add_cascade(label="File", menu=self.filemenu)
        
        self.parent.config(menu=self.menubar)
        
    def savedata(self):
        """ Save DataFrame to file. """
        options = {}
        options['initialdir'] = '{0}'.format(os.path.expanduser('~'))
        options['filetypes'] = [('Excel Spreadsheet', '.xlsx'),
                                ('HTML Table','.html'),
                                ('LaTeX Tabular environment', '.tex'),
                                ('Comma-Separated variable (CSV)', '.csv')
                                ]
        options['title'] = 'Save Data As'
        options['defaultextension'] = '.csv'
        options['parent'] = self.parent
        
        f = tkFileDialog.asksaveasfilename(**options)
        if f is None or len(f) == 0:
            return
        
        # Output 'all' sframe to file depending on file extension
        ext = os.path.splitext(f)[1]
        if ext == '.csv':
            self.sframe.to_csv(f)
        elif ext == '.xlsx':
            self.sframe.to_excel(f)
        elif ext == '.tex':
            self.sframe.to_latex(f)
        elif ext == '.html':
            self.sframe.to_html(f)
        else:
            tkMessageBox.showerror("Unknown file type", "Unknown file type *{0}".format(ext))
        
        
        
class LogDisplay(tk.Frame):
    """ Separate log window for messages """
    def __init__(self, parent):
        self.parent = parent
        tk.Frame.__init__(self, self.parent)
        
        self.vscroll = ttk.Scrollbar(self, orient=tk.VERTICAL)
        self.hscroll = ttk.Scrollbar(self, orient=tk.HORIZONTAL)
        self.console = tk.Text(self, wrap='none', width=60)
        
        self.console.config(yscrollcommand = self.vscroll.set)
        self.console.config(xscrollcommand = self.hscroll.set)
        self.vscroll.config(command = self.console.yview)
        self.hscroll.config(command = self.console.xview)
        
        self.console.grid(column=0,row=0, sticky=(tk.W, tk.N, tk.S, tk.E))
        self.vscroll.grid(column=1, row=0, sticky=(tk.E,tk.N,tk.S))
        self.hscroll.grid(column=0,row=1, sticky=(tk.E,tk.W,tk.S))
        
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.console.insert(tk.END, 'Started PIEFACE GUI\n*************************\n')
        self.console.config(state=tk.DISABLED)
        
class LoggingtoGUI(logging.Handler):
    """ Redirect logging to console """
    def __init__(self, console):
        logging.Handler.__init__(self)
        self.console = console
    
    def emit(self, message):
        formattedMessage = self.format(message)
        self.console.config(state = tk.NORMAL)
        self.console.insert(tk.END, formattedMessage+'\n')
        self.console.config(state=tk.DISABLED)
        self.console.see(tk.END)
        
class CritFilter(logging.Filter):
    def filter(self, rec):
        if rec.levelno == logging.CRITICAL:
            # Call raise_message if rec is critical
            root.after(1, raise_message, rec)
            return True
        else:
            return True
            
def raise_message(log):
    if "Label(s) %s are not present" in log.msg:
        box = tk.Toplevel(root)
        box.title('Error')
        message = ttk.Label(box, text = log.msg % log.args)
        labels = {}
        for f in app.filenames:
            labels[os.path.basename(f)] = " ".join(sorted(multiCIF._alllabels(f)))
        advice = ttk.Label(box, text = "Valid labels are:\n{0}".format( "".join( ["{0:40s}: {1:30s}\n".format(p, labels[p]) for p in labels] )))
        tip = ttk.Label(box, text="[ Tip: Regular expressions can also be used to centre labels ]")
        button = ttk.Button(box, text='OK', command= lambda: box.destroy())
        message.grid(row = 0, padx = 5, pady = 5)
        advice.grid(row = 1, padx = 5, pady = 5)
        tip.grid(row=2, padx=5, pady=5)
        button.grid(row = 3, padx = 5, pady = 5)
        root.wait_window(window=box)
    else:
        pass
        
    #tkMessageBox.showerror('Error',log.msg)
        
def multiCIF_start(args, kwargs):
    """ Wrapper to start listener queue for logging, and then create process to start multiCIF_wrapper """

    queue = multiprocessing.Queue(-1)
    lp = threading.Thread(target = multiCIF.listener_process, args=(queue, multiCIF.listener_empty_config,))
    lp.start()
    p = multiprocessing.Process(target = multiCIF_wrapper,
                                  args = (queue, args,),
                                  kwargs = kwargs)
    return p, lp, queue
def multiCIF_stop(process, listener, queue):
    """ Stop multiprocess, and safely end logging listener """
    process.terminate()
    process.join()
    queue.put_nowait(None)
    listener.join()   
def multiCIF_wrapper(queue, args, **kwargs):
    """ Wrapper for multiCIF.main to start logging to QueueHandler, before starting multiCIF.main """
    root = logging.getLogger()
    h = multiCIF.QueueHandler(queue)
    root.addHandler(h)
    root.setLevel(logging.DEBUG)
    multiCIF.main(*args, **kwargs)    
    
def multiCIF_thread_wrapper(*args, **kwargs):
    """ Wrapper to put results of multiCIF into a queue to be retrieved """
    queue = args[0]
    calling_win = args[1]
    try:
        results = multiCIF.main(*args[2:], **kwargs)
        queue.put(results)
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        queue.put(sys.exc_info())
        queue.put_nowait(None)
        #raise
        #calling_win.report_callback_exception(exc_type, exc_value, exc_traceback)
        #root_win.after(5, tkMessageBox.showerror, "Error", " ".join(e.args))
        

def main():
    if sys.platform.startswith('win'):
        # Hack for multiprocessing.freeze_support() to work from a
        # setuptools-generated entry point.
        multiprocessing.freeze_support()
        
    root = tk.Tk()
    root.minsize(450,380)    #width,height
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    
    root.iconbitmap(iconloc)
    
    app = MainWindow(root)
    

    h = LoggingtoGUI(app.log.console)
    h.setLevel(logging.INFO)
    f = CritFilter()
    h.addFilter(f)
    log.addHandler(h)
    
    #log.addFilter(f)
    root.mainloop()
    
if __name__ == '__main__':
    main()
