""" Tests for multiCIF.py """
import unittest
from distellipsoid import multiCIF
import numpy as np

# Minimal 
simpleCIF="""
"""



class LabelChecking(unittest.TestCase):
    """ Test processing of site labels for centre/ligands using check_labels(). """
    
    def setUp(self):
        """ Set up simple labels/types for testing check_labels. """
        self.alllabels = ['Pr1','O1','O2','O3','Al1','Pr2']
        #self.cifs
        
    def tearDown(self):
        del(self.alllabels)
        
    def test_preciselabel(self):
        """ Test filtering by specific label names """
        check, omit, missing = multiCIF.check_labels(['Pr1','O3'], self.alllabels)
        self.assertItemsEqual(check, ['Pr1', 'O3'])
        self.assertItemsEqual(omit, [])
        self.assertItemsEqual(missing, [])
        
    def test_regexlabel(self):
        """ Test filtering by a wildcard regular expression """
        check, omit, missing = multiCIF.check_labels(['Pr1','O.*'], self.alllabels)
        self.assertItemsEqual(check, ['Pr1', 'O1','O2','O3'])
        self.assertItemsEqual(omit, [])
        self.assertItemsEqual(missing, [])
    
    def test_labelexclude(self):
        """ Test exclusion of labels using regex with check_labels """
        check, omit, missing = multiCIF.check_labels(['Pr1','#O.*'], self.alllabels)
        self.assertItemsEqual(check, ['Pr1'])
        self.assertItemsEqual(omit, ['O1','O2','O3'])
        self.assertItemsEqual(missing, [])
        
    def test_missing(self):
        """ Test return of unknown label"""
        check, omit, missing = multiCIF.check_labels(['Px1'], self.alllabels)
        self.assertItemsEqual(check, [])
        self.assertItemsEqual(omit, [])
        self.assertItemsEqual(missing, ['Px1'])


class DefineLigands(unittest.TestCase):
    """ Test generation of ligand types and labels to test based on supplied expressions """
    def SetUp(self):
        # Do some useful setting up before each test
        pass
    def TearDown(self):
        # Do some post-test cleanup after each test
        pass
    def test_liglabels(self):
        """ Test defining ligands using labels alone """
        self.CIFS = ['CIF1.cif','CIF2.cif']

        
if __name__ == "__main__":

    test_classes_to_run = [ LabelChecking,

                           ]
    
    

    suites_list = []
    for test_class in test_classes_to_run:
        suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suites_list.append(suite)

    big_suite = unittest.TestSuite(suites_list)

    results = unittest.TextTestRunner().run(big_suite)