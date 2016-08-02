""" Tests for polyhedron.py """
import unittest
from distellipsoid import readcoords
import numpy as np
import os
import StringIO         # Necessary to read text string like a file
import pkg_resources    # To find packaged CIF files

# Very basic CIF format to avoid problems opening files
simpleCIF = """
data_test
_cell_angle_alpha                55.65(2)
_cell_angle_beta                 55.65(2)
_cell_angle_gamma                55.65(2)
_cell_length_a                   5.740(1)
_cell_length_b                   5.740(1)
_cell_length_c                   5.740(1)
loop_
_atom_site_label
_atom_site_type_symbol
_atom_site_fract_x
_atom_site_fract_y
_atom_site_fract_z
Mn1 Mn2+ 0.3617    0.3617    0.3617
O1  O2-  0.0000    0.0000    0.0000

"""

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

class CifRead(unittest.TestCase):
    """ Check reading of CIF files works as expected. """
    # Mainly checks correct interface to pyCIFRW
    
    def setUp(self):
        """ Generate simple CIF objects. """
        # Find all 'test_data' files ending .cif, and create a dict with {filename:absolute path}
        testCIFS = dict([(f, pkg_resources.resource_filename('test_data', f)) for f in pkg_resources.resource_listdir('test_data','') if f.endswith('.cif')])
        self.textCIF = simpleCIF
        self.CIFS={}
        self.results = {}
        # Sample cif file expected results
        # Random COD cif files...
        self.CIFS['1004021'] = testCIFS['MnSnO3_COD1004021.cif']
        self.results['1004021'] = {}
        self.results['1004021']['cell'] = {'a':5.740, 'b':5.740, 'c':5.740, 'alp':55.65, 'bet':55.65, 'gam':55.65}
        self.results['1004021']['atomcoords'] = {'Mn1': np.array([0.3617, 0.3617, 0.3617]), 'Sn1': np.array([0.1512, 0.1512, 0.1512]), 'O1': np.array([0.557, -0.040, 0.227])}
        self.results['1004021']['atomtypes'] = {'Mn1':'Mn2+','Sn1':'Sn4+','O1':'O2-'}
        self.results['1004021']['spacegrp'] = '148'
        self.results['1004021']['symmops'] = ['x,y,z','y,z,x','z,x,y','-x,-y,-z','-y,-z,-x','-z,-x,-y']
        self.results['1004021']['symmid'] = [0,1,2,3,4,5]
        # 
        self.CIFS['1000064'] = testCIFS['fayalite_COD1000064.cif']
        self.results['1000064'] = {}
        self.results['1000064']['cell'] = {'a':4.8195, 'b':10.4788, 'c':6.0873, 'alp':90, 'bet':90, 'gam':90}
        self.results['1000064']['atomcoords'] = {'Fe1': np.array([0.0, 0.0, 0.0]),
                                                 'Fe2': np.array([0.98598, 0.28026, 0.25]),
                                                 'Si1': np.array([0.43122, 0.09765, 0.25]),
                                                 'O1': np.array([0.76814, 0.09217, 0.25]),
                                                 'O2': np.array([0.20895, 0.45365, 0.25]),
                                                 'O3': np.array([0.28897, 0.16563, 0.03643]),
                                                 }
        self.results['1000064']['atomtypes'] = {'Fe1':'Fe2+','Fe2':'Fe2+','Si1':'Si4+','O1':'O2-', 'O2':'O2-', 'O3':'O2-'}
        self.results['1000064']['spacegrp'] = '62'
        self.results['1000064']['symmops'] = ['x,y,z',
                                              '1/2-x,1/2+y,1/2-z',
                                              '-x,-y,1/2+z', 
                                              '1/2+x,1/2-y,-z', 
                                              '-x,-y,-z', 
                                              '1/2+x,1/2-y,1/2+z', 
                                              'x,y,1/2-z', 
                                              '1/2-x,1/2+y,z']
        self.results['1000064']['symmid'] = [0,1,2,3,4,5,6,7]
        
    def TearDown(self):
        del(self.CIFS)
        del(self.results)
        del(self.textCIF)
        
    def test_read_CIFS(self):
        """ Test CIF reads correctly"""
        for cif in self.CIFS:
            returnvals = readcoords.readcif(self.CIFS[cif])
            self.assertDictEqual(returnvals[0], self.results[cif]['cell'])
            # Test atomcoords are equal
            self.assertItemsEqual(returnvals[1].keys(), self.results[cif]['atomcoords'].keys())
            for k in returnvals[1].keys():
                np.testing.assert_array_almost_equal(returnvals[1][k], self.results[cif]['atomcoords'][k])
            self.assertDictEqual(returnvals[2], self.results[cif]['atomtypes'])
            self.assertEqual(returnvals[3], self.results[cif]['spacegrp'])
            self.assertListEqual(returnvals[4], self.results[cif]['symmops'])
            self.assertListEqual(returnvals[5], self.results[cif]['symmid'])
            
        
        

if __name__ == "__main__":

    test_classes_to_run = [ CrystalInit,
                            CifRead,
                           ]
    
    

    suites_list = []
    for test_class in test_classes_to_run:
        suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suites_list.append(suite)

    big_suite = unittest.TestSuite(suites_list)

    results = unittest.TextTestRunner().run(big_suite)