"""
Setup pieface on your system with setuptools
"""

from setuptools import setup, find_packages

def readme():
    with open('README.rst') as f:
        return f.read()

setup(
    name = "PIEFACE",
    version = "1.0.0",
    author = "James Cumby",
    author_email = "james.cumby@ed.ac.uk",
    url = "https://bitbucket.org/JCumby/pieface",
    description = ("A program for calculating minimum bounding ellipsoids for"
                "crystallographic polyhedra and various related properties"),
    license = "MIT",
    keywords = ["Polyhedra", "Crystallography", "Materials", "Analysis", "Distortion"],
    long_description=readme(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Natural Language :: English",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT license",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
    ],
    
    packages = find_packages(),
    include_package_data = True,
    install_requires = ['numpy>=1.9.2',
                        'matplotlib>=1.4.3',
                        'PyCifRW>=3.3',
                        'multiprocessing>=2.6.2.1',
                        'pandas>=0.17.1',
                        
    ],
    test_suite = 'tests',
    package_data = {
        'pieface' : ['README.rst'],
        'test_files': ['test_data/*.cif'],
        },
    entry_points = {
        'console_scripts' : [
            'CIFellipsoid=pieface.CIFellipsoid:main'],
        'gui_scripts':[
            'EllipsoidGUI=pieface.pieface_gui:main'],
            }
                        
    
)    