""" Tests for polyhedron.py """
import unittest
from distellipsoid import readcoords
import numpy as np

class CrystalInit(unittest.TestCase):
    """ Test initialisation of simple Crystal object"""
    cell = {'a'     :5,
            'b'     :5,
            'c'     :5,
            'alp'   :90,
            'bet'   :90,
            'gam'   :90}
            
    def TearDown(self):
        del(self.Crystal)
    
    def test_celldict(self):
        """ Test intialising with dictionary of lattice parameters """
        self.Crystal = readcoords.Crystal(cell=self.cell, atoms=None, atomtypes=None)
        self.assertEqual(self.Crystal.cell, self.cell)
        
    def test_celllist(self):
        """ Test intialising with list of lattice parameters """
        self.Crystal = readcoords.Crystal(cell=[self.cell['a'], self.cell['b'], self.cell['c'], self.cell['alp'],self.cell['bet'],self.cell['gam']], atoms=None, atomtypes=None)
        self.assertEqual(self.Crystal.cell, self.cell)
        
    def test_cellstring(self):
        """ Test intialising with string of lattice parameters """
        self.Crystal = readcoords.Crystal(cell=str(self.cell['a'])+" "+\
                                               str(self.cell['b'])+" "+\
                                               str(self.cell['c'])+" "+\
                                               str(self.cell['alp'])+" "+\
                                               str(self.cell['bet'])+" "+\
                                               str(self.cell['gam']), atoms=None, atomtypes=None)
        self.assertEqual(self.Crystal.cell, self.cell)    

if __name__ == "__main__":

    test_classes_to_run = [ CrystalInit,

                           ]
    
    

    suites_list = []
    for test_class in test_classes_to_run:
        suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suites_list.append(suite)

    big_suite = unittest.TestSuite(suites_list)

    results = unittest.TextTestRunner().run(big_suite)