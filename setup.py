"""
Setup distellipsoid on your system with setuptools
"""

from setuptools import setup, find_packages

setup(
    name = "distellipsoid",
    version = "0.3.1a",
    revision = "$Revision$",
    author = "James Cumby",
    author_email = "james.cumby@ed.ac.uk",
    description = ("A program for calculating minimum bounding ellipsoids for"
                "crystallographic polyhedra and various related properties"),
    license = "Unknown",
    keywords = "Polyhedra Crystallography Materials Analysis Distortion",
    long_description=('README'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: None :: None",
        "Programming Language :: Python :: 2.7",
    ],
    
    packages = find_packages(),
    install_requires = ['numpy>=1.9.2',
                        'matplotlib>=1.4.3',
                        'PyCifRW>=3.3',
                        'multiprocessing>=2.6.2.1',
                        'pandas>=0.17.1',
                        
    ],
    test_suite = 'tests',
    entry_points = {
        'console_scripts' : [
            'CIFellipsoid=distellipsoid.CIFellipsoid:main'],
        'gui_scripts':[
            'EllipsoidGUI=distellipsoid.distellipsoid_gui:main'],
            }
                        
    
)    