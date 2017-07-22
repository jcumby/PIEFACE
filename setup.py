"""
Setup pieface on your system with setuptools
"""

from setuptools import setup, find_packages

def readme():
    with open('README.rst') as f:
        return f.read()

setup(
    name = "pieface",
    version = "1.1.0",
    author = "James Cumby",
    author_email = "james.cumby@ed.ac.uk",
    url = "https://github.com/jcumby/PIEFACE",
    description = ("A program for calculating minimum bounding ellipsoids for"
                "crystallographic polyhedra and various related properties"),
    license = "MIT",
    keywords = ["Polyhedra", "Crystallography", "Materials", "Analysis", "Distortion"],
    long_description=readme(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Natural Language :: English",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
    ],
    
    packages = find_packages(),
    include_package_data = False,
    setup_requires = ['numpy'],
    install_requires = ['numpy>=1.9.2',
                        'matplotlib>=1.4.3',
                        'pycifrw>=4.2',
                        'multiprocessing>=2.6.2.1',
                        'pandas>=0.17.1',
                        
    ],
    test_suite = 'pieface.tests',
    package_data = {
        'pieface' : ['data/pieface.png', 'data/pieface.ico', 'data/pieface.xbm'],
        'pieface.tests': ['test_data/*.cif'],
        },
    entry_points = {
        'console_scripts' : [
            'CIFellipsoid=pieface.CIFellipsoid:main'],
        'gui_scripts':[
            'EllipsoidGUI=pieface.pieface_gui:main'],
            }
                        
    
)    