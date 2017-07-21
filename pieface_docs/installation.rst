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

    pip install PIEFACE

or alternatively by manually :ref:`installing from sources <sources>`. 

.. note:: The PyPI version is currently exhibiting issues resolving dependencies correctly with ``pip``. See :ref:`known issues <issues>` for details.


In reality, installation can sometimes be operating-system specific.

Updates
^^^^^^^

From version 1.1.0, |pieface| now includes automatic update checking. From |GUI| go to :menuselection:`Help --> Check for Updates` and follow the dialogue boxes. From |cmdprog|, 
type |cmdprog|``-V`` and follow the resulting link.

.. _windows:

Windows
^^^^^^^

Due to problems with ensuring correct dependencies, the recommended method for obtaining |pieface| for Windows is to download the most recent self-contained installer
|wininstall|_ and run it, following the on-screen prompts. This will also (optionally) add |pieface| shortcuts to the Start Menu and Windows Desktop,
as well as making the two main scripts accessible from the Windows Command Line (cmd).

The installer comes packaged with a minimal Python runtime environment, therefore this installer will work without (and not interfere with an existing) |Python|
installation.

.. _macosx:

MAC OS X
^^^^^^^^

Unfortunately |pieface| is not currently available as a pre-built MAC distribution, as the author does not have access to that operating system!

If |Python| is available from the terminal, 
installing may be as simple as::

    pip install PIEFACE

or installing from :ref:`sources <setup>`. If this does not work, see :ref:`issues`.


.. _linux:

Linux derivatives
^^^^^^^^^^^^^^^^^

Unix-like operating systems generally come with a version of Python included. In this case::
    
    pip install PIEFACE
    
should work, but may require some manual installation of dependencies (see :ref:`issues`).


.. _sources:

Installation from Sources
-------------------------


Stable Build
^^^^^^^^^^^^

|pieface| can also be installed from the source distribution. The current release is available from the `PIEFACE repository <https://github.com/jcumby/PIEFACE>`_. 
Once downloaded, this file should be unpacked into the desired directory (``tar -xzf pieface_1.0.0.tar.gz``) before following the :ref:`manual install instructions <setup>`.

.. _setup:

Manual Install
^^^^^^^^^^^^^^

Once the source code has been downloaded, it is then necessary to install it using Python from within the 
main |pieface| directory::

    python setup.py install

This *should* collect all dependencies, and compile them if necessary. If this fails, it may be necessary to install :ref:`dependencies <requirements>` manually first,
before running ``python setup.py install`` again.

.. _development:

Development Version
^^^^^^^^^^^^^^^^^^^

The latest development version of |pieface| can be obtained from the `PIEFACE repository <https://github.com/jcumby/PIEFACE>`_ using `git <https://git-scm.com/>`_::

    git clone https://github.com/jcumby/PIEFACE .

To update the repository at a later date, use::

    git pull
    
In both cases, you should then change into the resulting directory, and follow the instruction for :ref:`manual install <setup>`.


.. requirements:

Requirements
------------

* `Python 2.7 <https://www.python.org/>`_ (currently NOT Python 3)
* `NumPy <http://www.numpy.org>`_ (at least version 1.9)
* `matplotlib <http://matplotlib.org/>`_ (1.4.3 or higher)
* `PyCifRW <https://bitbucket.org/jamesrhester/pycifrw/overview>`_ (4.2 or higher)
* `multiprocessing <https://docs.python.org/2/library/multiprocessing.html>`_ (2.6.2 or higher)
* `pandas <http://pandas.pydata.org/>`_ (0.17 or higher)


.. _issues:

Known Issues
------------

When installing using ``pip``, dependencies on PyCifRW and Matplotlib are not always resolved when using::

    pip install PIEFACE
    
In this case, there are a number of possible solutions:

    * Update pip (this can sometimes solve the problem)
 
    * Install the dependencies manually first::

        pip install PyCIFRW>=3.3
        pip install maplotlib>=1.4.3
    
    followed by ``pip install PIEFACE``
    
    * Manually download either the wheel (PIEFACE-X.X.X.whl) or compressed package (PIEFACE-X.X.X.zip or PIEFACE-X.X.X.tar.gz) from `PyPI <https://pypi.python.org/pypi>`_, and then install that::
    
        pip install PIEFACE-X.X.X.whl
        
    * Install from :ref:`sources <setup>` (may require compilation of other packages)
    

-------
Testing
-------

The package contains some basic unit tests, which can be run following installation either from source or using ``pip``. 
Tests can be run from within the main |pieface| directory with the command::

    python setup.py test
    
or alternatively from within a python prompt::

    import pieface
    pieface.self_test()

All tests should pass without exceptions - if not, please send me a bug report.

-------
Run It!
-------

Once correctly installed, the easiest way to access |pieface| is using either |GUI| or |cmdprog| (see :ref:`tutorials`).

    
