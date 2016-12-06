.. _installation:

Installation
============

|pieface|_ is written in pure |Python|_. While this makes it highly transferrable between operating systems,
it does require a number of other |Python| packages to operate.

----------
Installing
----------

Detailed installation instructions specific to different operating systems can be found under :ref:`windows`, :ref:`macosx` and :ref:`linux`.

|pieface| is registered on `PyPI <https://pypi.python.org/pypi>`_, therefore if you already have a working |Python| distribution, installation may be
as simple as::

    pip install pieface

or alternatively by manually downloading and installing:

* Download ``pieface.tar.gz`` to your computer
* Unpack to a local directory
* Install using::

        python setup.py install
        
        
In reality, installation can sometimes be operating-system specific.

.. _windows:

Windows
^^^^^^^

Due to problems with ensuring correct dependencies, the recommended method for obtaining |pieface| for Windows is to download the most recent self-contained installer
|wininstall|_ and run it, following the on-screen prompts. This will also (optionally) add |pieface| shortcuts to the Start Menu and Windows Desktop,
as well as making the two main scripts accessible from the Windows Command Line.

The installer comes packaged with a minimal Python runtime environment, therefore this installer will work without (and not interfere with an existing) |Python|
installation.

.. _macosx:

MAC OS X
^^^^^^^^

Unfortunately |pieface| is not currently available as a pre-built MAC distribution, as the author does not have access to that operating system!

Installing using the simple ``pip`` or ``python setup.py install`` routes may be possible using the default Python environment...

.. _linux:

Linux derivatives
^^^^^^^^^^^^^^^^^

Unix-like operating systems generally come with python included. In this case,::
    
    pip install pieface
    
should work as expected.

------------
Requirements
------------

* `Python 2.7 <https://www.python.org/>`_ (currently NOT Python 3)
* `NumPy <http://www.numpy.org>`_ (at least version 1.9)
* `matplotlib <http://matplotlib.org/>`_ (1.4.3 or higher)
* `PyCifRW <https://bitbucket.org/jamesrhester/pycifrw/overview>`_ (3.3 or higher)
* `multiprocessing <https://docs.python.org/2/library/multiprocessing.html>`_ (2.6.2 or higher)
* `pandas <http://pandas.pydata.org/>`_ (0.17 or higher)


-------------------------
Installation from Sources
-------------------------


Stable Build
^^^^^^^^^^^^

|pieface| can also be installed from the source distribution. The current release is available from the `PIEFACE repository <https://github.com/jcumby/PIEFACE>`_. 
Once downloaded, this file should be unpacked into the desired directory (``tar -xzf pieface_1.0.0.tar.gz``) before following the :ref:`setup instructions <setup>`.


Development Version
^^^^^^^^^^^^^^^^^^^

The latest development version of |pieface| can be obtained from the `PIEFACE repository <https://github.com/jcumby/PIEFACE>`_ using `git <https://git-scm.com/>`::

    git clone https://github.com/jcumby/PIEFACE .

To update the repository at a later date, use::

    git pull
    
In both cases, you should then change into the resulting directory, and follow the instruction for :ref:`manual install <setup>`.

.. _setup:

Manual Install
^^^^^^^^^^^^^^

Once the source code has been downloaded, it is then necessary to install it using Python from within the 
main |pieface| directory::

    python setup.py install

This may require all dependencies to already be installed.    

-------
Testing
-------

The package contains some basic unit tests, which can be run from within the main |pieface| directory with the command::

    python setup.py test

All tests should pass without exceptions - if not, please send me a bug report.

-------
Run It!
-------

Once correctly installed, the easiest way to access |pieface| is using either |GUI| or |cmdprog| (see :ref:`tutorials`).
