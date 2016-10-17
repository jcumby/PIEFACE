""" Tests for polyhedron.py """
import unittest
from pieface import polyhedron
import numpy as np

class RepeatedPolyFunctions(object):
    """ Methods to test polyhedron functions with repeated values, assumes initialisation will work. """
    @classmethod
    def setUpClass(cls):
        """Initialise Polyhedron object."""
        cls.poly = polyhedron.Polyhedron(centre=cls.centre, ligands = cls.ligands, atomdict = cls.atomdict, ligtypes = cls.ligtypes)
    @classmethod
    def tearDownClass(cls):
        """ Delete polyhedron object. """
        del(cls.poly)
    
    # Tests for Polyhedron attributes
    def test_ligabc(self):
        np.testing.assert_almost_equal(self.poly.ligabc, self.valid['ligabc'])
    def test_cenabc(self):
        np.testing.assert_almost_equal(self.poly.cenabc, self.valid['cenabc'])
    def test_liglbl(self):
        self.assertEqual(self.poly.liglbl, self.valid['liglbl'])
    def test_cenlbl(self):
        self.assertEqual(self.poly.cenlbl, self.valid['cenlbl'])
    def test_allabc(self):
        np.testing.assert_almost_equal(self.poly.allabc, self.valid['allabc'])
    def test_alllbl(self):
        self.assertEqual(self.poly.alllbl, self.valid['alllbl'])
    def test_ligtyp(self):
        self.assertEqual(self.poly.ligtyp, self.valid['ligtyp'])
    def test_centyp(self):
        self.assertEqual(self.poly.centyp, self.valid['centyp'])
        
    def test_cenxyz(self):
        np.testing.assert_almost_equal(self.poly.cenxyz(self.ortho), self.valid['cenxyz'])
    def test_ligxyz(self):
        np.testing.assert_almost_equal(self.poly.ligxyz(self.ortho), self.valid['ligxyz'])
    def test_allxyz(self):
        np.testing.assert_almost_equal(self.poly.allxyz(self.ortho), self.valid['allxyz'])
    def test_ligdelxyz(self):
        np.testing.assert_almost_equal(self.poly.ligdelxyz(self.ortho), self.valid['ligdelxyz'])
    def test_alldelxyz(self):
        np.testing.assert_almost_equal(self.poly.alldelxyz(self.ortho), self.valid['alldelxyz'])
    def test_ligdelabc(self):
        np.testing.assert_almost_equal(self.poly.ligdelabc(), self.valid['ligdelabc'])
    def test_alldelabc(self):
        np.testing.assert_almost_equal(self.poly.alldelabc(), self.valid['alldelabc'])
    def test_allbondlens(self):
        np.testing.assert_almost_equal(self.poly.allbondlens(self.M), self.valid['allbondlens'])
    def test_averagebondlen(self):
        np.testing.assert_almost_equal(self.poly.averagebondlen(self.M), self.valid['averagebondlen'])
    def test_pointcolours(self):
        self.assertEqual(self.poly.pointcolours(), self.valid['pointcolours'])
        

class EmptyCentreDictInit(unittest.TestCase):
    """ Test empty centre initialisation as dict (no atomdict)"""
    def test_init(self):
        centre = {}
        ligands = [('O1', [0.1,0,0]),
                   ('O2', [-0.1,0,0]),
                   ('O3', [0,0.1,0]),
                   ('O4', [0,-0.1,0]),
                   ('O5', [0,0,0.1]),
                   ('O6', [0,0,-0.1])]
          
        ligtypes = ['Mn','O','O','O','O','O','O']
        
        self.assertRaises(ValueError, polyhedron.Polyhedron, centre = centre, ligands = ligands, atomdict=None, ligtypes = ligtypes)
    def TearDown(self):
        del(self.poly)   
        
class EmptyCentreListInit(unittest.TestCase):
    """ Test empty centre initialisation as list (no atomdict)"""
    def test_init(self):
        centre = []
        ligands = [('O1', [0.1,0,0]),
                   ('O2', [-0.1,0,0]),
                   ('O3', [0,0.1,0]),
                   ('O4', [0,-0.1,0]),
                   ('O5', [0,0,0.1]),
                   ('O6', [0,0,-0.1])]
                             
        ligtypes = ['Mn','O','O','O','O','O','O']
        
        self.assertRaises(ValueError, polyhedron.Polyhedron, centre = centre, ligands = ligands, atomdict=None, ligtypes = ligtypes)
    def TearDown(self):
        del(self.poly) 

class InitFromDictsLigTypeList(unittest.TestCase):
    """ Test initialisation from name/coordinate dicts with ligand types as list"""
    def test_init(self):
        centre = ('Mn', [0,0,0])
        ligands = [('O1', [0.1,0,0]),
                   ('O2', [-0.1,0,0]),
                   ('O3', [0,0.1,0]),
                   ('O4', [0,-0.1,0]),
                   ('O5', [0,0,0.1]),
                   ('O6', [0,0,-0.1])]
        ligtypes = ['Mn','O','O','O','O','O','O']
        self.poly = polyhedron.Polyhedron(centre = centre, ligands = ligands, atomdict=None, ligtypes = ligtypes)
    def TearDown(self):
        del(self.poly)

class InitFromDictsLigTypeDict(unittest.TestCase):
    """ Test initialisation from name/coordinate tuples with ligand types as dict"""
    def test_init(self):
        centre = ('Mn', [0,0,0])
        ligands = [('O1', [0.1,0,0]),
                   ('O2', [-0.1,0,0]),
                   ('O3', [0,0.1,0]),
                   ('O4', [0,-0.1,0]),
                   ('O5', [0,0,0.1]),
                   ('O6', [0,0,-0.1])]
        ligtypes = {'Mn':'Mn','O1':'O','O2':'O','O3':'O','O4':'O','O5':'O','O6':'O'}
        self.poly = polyhedron.Polyhedron(centre = centre, ligands = ligands, atomdict=None, ligtypes = ligtypes)
    def TearDown(self):
        del(self.poly)    

class InitFromStringsAtomDict(unittest.TestCase):
    """ Initialise from name strings and atom dict (extra items in dict) """
    def test_init(self):
        centre = 'Mn'
        ligands = ['O1','O2','O3','O4','O5','O6']
        atomdict = {'O1': np.array([0.1,0,0]),
                   'O2': np.array([-0.1,0,0]),
                   'O3': np.array([0,0.1,0]),
                   'O4': np.array([0,-0.1,0]),
                   'O5': np.array([0,0,0.1]),
                   'O6': np.array([0,0,-0.1]),
                   'S1': np.array([5,5,5])
                   }   

class EmptyCentreStringInit(unittest.TestCase):
    """ Test initialisation with empty centre string and atomdict """
    def test_init(self):
        centre = ''
        ligands = ['O1','O2','O3','O4','O5','O6']
        atomdict = {'O1': np.array([0.1,0,0]),
                   'O2': np.array([-0.1,0,0]),
                   'O3': np.array([0,0.1,0]),
                   'O4': np.array([0,-0.1,0]),
                   'O5': np.array([0,0,0.1]),
                   'O6': np.array([0,0,-0.1]),
                   'S1': np.array([5,5,5])
                   }   
        ligtypes = ['Mn','O','O','O','O','O','O']
                
        self.assertRaises(TypeError, polyhedron.Polyhedron, centre = centre, ligands = ligands, atomdict=atomdict, ligtypes = ligtypes)

class NoLigandsAsList(RepeatedPolyFunctions, unittest.TestCase):
    """ Test empty ligand initialisation as list (no atomdict)"""

    # Parameters for setting up Polyhedron
    centre = ('Mn', [0,0,0])
    ligands = []
    atomdict = None
    ligtypes = {'Mn':'Mn'}

    # Parameters for tests
    ortho = np.array([[1,0,0],[0,1,0],[0,0,1]])
    M = np.array([[1,0,0],[0,1,0],[0,0,1]])
    
    # Correct values
    valid = { 'ligabc'      : np.array([[]]).T,
              'cenabc'      : np.array([0,0,0]),
              'liglbl'      : [],
              'cenlbl'      : 'Mn',
              'allabc'      : np.array([[0,0,0]]),
              'alllbl'      : ['Mn'],
              'ligtyp'      : [],
              'centyp'      : 'Mn',
              
              'cenxyz'      : np.array([0,0,0]),
              'ligxyz'      : np.array([[]]),
              'allxyz'      : np.array([[0,0,0]]),
              'ligdelxyz'   : np.array([[]]),
              'alldelxyz'   : np.array([[0,0,0]]),
              'ligdelabc'   : np.array([[]]),
              'alldelabc'   : np.array([[0,0,0]]),
              'allbondlens' : np.array([[]]),
              'averagebondlen': np.nan,
              'pointcolours': 'b'
            } 
        
class NoLigandsAsDict(RepeatedPolyFunctions, unittest.TestCase):
    """ Test empty ligand initialisation as list (no atomdict)"""

    # Parameters for setting up Polyhedron
    centre = {'Mn': [0,0,0]}
    ligands = {}
    atomdict = None
    ligtypes = {'Mn':'Mn'}

    # Parameters for tests
    ortho = np.array([[1,0,0],[0,1,0],[0,0,1]])
    M = np.array([[1,0,0],[0,1,0],[0,0,1]])
    
    # Correct values
    valid = { 'ligabc'      : np.array([[]]).T,
              'cenabc'      : np.array([0,0,0]),
              'liglbl'      : [],
              'cenlbl'      : 'Mn',
              'allabc'      : np.array([[0,0,0]]),
              'alllbl'      : ['Mn'],
              'ligtyp'      : [],
              'centyp'      : 'Mn',
              
              'cenxyz'      : np.array([0,0,0]),
              'ligxyz'      : np.array([[]]),
              'allxyz'      : np.array([[0,0,0]]),
              'ligdelxyz'   : np.array([[]]),
              'alldelxyz'   : np.array([[0,0,0]]),
              'ligdelabc'   : np.array([[]]),
              'alldelabc'   : np.array([[0,0,0]]),
              'allbondlens' : np.array([[]]),
              'averagebondlen': np.nan,
              'pointcolours': 'b'
            } 
 
class NoLigandsAsAtomDict(RepeatedPolyFunctions, unittest.TestCase):
    """ Test empty ligand initialisation as list (no atomdict)"""

    # Parameters for setting up Polyhedron
    centre = 'Mn'
    ligands = []
    atomdict = {'Mn': np.array([0,0,0]),
                'O1': np.array([0.1,0,0]),
                'O2': np.array([-0.1,0,0]),
                'O3': np.array([0,0.1,0]),
                'O4': np.array([0,-0.1,0]),
                'O5': np.array([0,0,0.1]),
                'O6': np.array([0,0,-0.1])
                } 
    ligtypes = ['Mn']

    # Parameters for tests
    ortho = np.array([[1,0,0],[0,1,0],[0,0,1]])
    M = np.array([[1,0,0],[0,1,0],[0,0,1]])
    
    # Correct values
    valid = { 'ligabc'      : np.array([[]]).T,
              'cenabc'      : np.array([0,0,0]),
              'liglbl'      : [],
              'cenlbl'      : 'Mn',
              'allabc'      : np.array([[0,0,0]]),
              'alllbl'      : ['Mn'],
              'ligtyp'      : [],
              'centyp'      : 'Mn',
              
              'cenxyz'      : np.array([0,0,0]),
              'ligxyz'      : np.array([[]]),
              'allxyz'      : np.array([[0,0,0]]),
              'ligdelxyz'   : np.array([[]]),
              'alldelxyz'   : np.array([[0,0,0]]),
              'ligdelabc'   : np.array([[]]),
              'alldelabc'   : np.array([[0,0,0]]),
              'allbondlens' : np.array([[]]),
              'averagebondlen': np.nan,
              'pointcolours': 'b'
            }
 
class SimpleOctahedronAsList(RepeatedPolyFunctions, unittest.TestCase):
    """ Tests for polyhedron methods, based on simple octahedron """

    # Parameters for setting up Polyhedron
    centre = ('Mn', [0,0,0])
    ligands = [('O1', [0.1,0,0]),
               ('O2', [-0.1,0,0]),
               ('O3', [0,0.1,0]),
               ('O4', [0,-0.1,0]),
               ('O5', [0,0,0.1]),
               ('O6', [0,0,-0.1])]
    atomdict = None
    ligtypes = {'Mn':'Mn','O1':'O','O2':'O','O3':'O','O4':'O','O5':'O','O6':'O'}

    # Parameters for tests
    ortho = np.array([[1,0,0],[0,1,0],[0,0,1]])
    M = np.array([[1,0,0],[0,1,0],[0,0,1]])

    # Constants holding often-repeated results
    abcxyz = np.array([[0,0,0],\
                       [0.1,0,0],\
                       [-0.1,0,0],\
                       [0,0.1,0],\
                       [0,-0.1,0],\
                       [0,0,0.1],\
                       [0,0,-0.1]])
    
    # Correct values
    valid = { 'ligabc'      : abcxyz[1:],
              'cenabc'      : abcxyz[0],
              'liglbl'      : ['O1','O2','O3','O4','O5','O6'],
              'cenlbl'      : 'Mn',
              'allabc'      : abcxyz,
              'alllbl'      : ['Mn','O1','O2','O3','O4','O5','O6'],
              'ligtyp'      : ['O','O','O','O','O','O'],
              'centyp'      : 'Mn',
              
              'cenxyz'      : abcxyz[0],
              'ligxyz'      : abcxyz[1:],
              'allxyz'      : abcxyz,
              'ligdelxyz'   : abcxyz[1:],
              'alldelxyz'   : abcxyz,
              'ligdelabc'   : abcxyz[1:],
              'alldelabc'   : abcxyz,
              'allbondlens' : np.array([0.1,0.1,0.1,0.1,0.1,0.1]),
              'averagebondlen': 0.1,
              'pointcolours': ['b', 'r','r','r','r','r','r']
            }
              
class SimpleOctahedronAsDict(RepeatedPolyFunctions, unittest.TestCase):
    """ Tests for polyhedron methods, based on simple octahedron """

    # Parameters for setting up Polyhedron
    centre = {'Mn': [0,0,0]}
    ligands = {'O1': [0.1,0,0],
               'O2': [-0.1,0,0],
               'O3': [0,0.1,0],
               'O4': [0,-0.1,0],
               'O5': [0,0,0.1],
               'O6': [0,0,-0.1]}
    atomdict = None
    ligtypes = {'Mn':'Mn','O1':'O','O2':'O','O3':'O','O4':'O','O5':'O','O6':'O'}

    # Parameters for tests
    ortho = np.array([[1,0,0],[0,1,0],[0,0,1]])
    M = np.array([[1,0,0],[0,1,0],[0,0,1]])

    # Constants holding often-repeated results
    abcxyz = np.array([[0,0,0],\
                       [0.1,0,0],\
                       [-0.1,0,0],\
                       [0,0.1,0],\
                       [0,-0.1,0],\
                       [0,0,0.1],\
                       [0,0,-0.1]])
    
    # Correct values
    valid = { 'ligabc'      : abcxyz[1:],
              'cenabc'      : abcxyz[0],
              'liglbl'      : ['O1','O2','O3','O4','O5','O6'],
              'cenlbl'      : 'Mn',
              'allabc'      : abcxyz,
              'alllbl'      : ['Mn','O1','O2','O3','O4','O5','O6'],
              'ligtyp'      : ['O','O','O','O','O','O'],
              'centyp'      : 'Mn',
              
              'cenxyz'      : abcxyz[0],
              'ligxyz'      : abcxyz[1:],
              'allxyz'      : abcxyz,
              'ligdelxyz'   : abcxyz[1:],
              'alldelxyz'   : abcxyz,
              'ligdelabc'   : abcxyz[1:],
              'alldelabc'   : abcxyz,
              'allbondlens' : np.array([0.1,0.1,0.1,0.1,0.1,0.1]),
              'averagebondlen': 0.1,
              'pointcolours': ['b', 'r','r','r','r','r','r']
            } 

class SimpleOctahedronAsAtomDict(RepeatedPolyFunctions, unittest.TestCase):
    """ Tests for polyhedron methods, based on simple octahedron """

    # Parameters for setting up Polyhedron
    centre = 'Mn'
    ligands = ('O1','O2','O3','O4','O5','O6')
    atomdict = {'Mn': np.array([0,0,0]),
                'O1': np.array([0.1,0,0]),
                'O2': np.array([-0.1,0,0]),
                'O3': np.array([0,0.1,0]),
                'O4': np.array([0,-0.1,0]),
                'O5': np.array([0,0,0.1]),
                'O6': np.array([0,0,-0.1])
                } 
    ligtypes = ['Mn','O','O','O','O','O','O']

    # Parameters for tests
    ortho = np.array([[1,0,0],[0,1,0],[0,0,1]])
    M = np.array([[1,0,0],[0,1,0],[0,0,1]])

    # Constants holding often-repeated results
    abcxyz = np.array([[0,0,0],\
                       [0.1,0,0],\
                       [-0.1,0,0],\
                       [0,0.1,0],\
                       [0,-0.1,0],\
                       [0,0,0.1],\
                       [0,0,-0.1]])
    
    # Correct values
    valid = { 'ligabc'      : abcxyz[1:],
              'cenabc'      : abcxyz[0],
              'liglbl'      : ['O1','O2','O3','O4','O5','O6'],
              'cenlbl'      : 'Mn',
              'allabc'      : abcxyz,
              'alllbl'      : ['Mn','O1','O2','O3','O4','O5','O6'],
              'ligtyp'      : ['O','O','O','O','O','O'],
              'centyp'      : 'Mn',
              
              'cenxyz'      : abcxyz[0],
              'ligxyz'      : abcxyz[1:],
              'allxyz'      : abcxyz,
              'ligdelxyz'   : abcxyz[1:],
              'alldelxyz'   : abcxyz,
              'ligdelabc'   : abcxyz[1:],
              'alldelabc'   : abcxyz,
              'allbondlens' : np.array([0.1,0.1,0.1,0.1,0.1,0.1]),
              'averagebondlen': 0.1,
              'pointcolours': ['b', 'r','r','r','r','r','r']
            }
            
class FullColourPalette(unittest.TestCase):
    """ Test full range of point colours """
    def setUp(self):
        """Initialise empty ellipsoid object and find ellipsoid (assumes findellipsoid() is ok)."""
        self.centre = ('Mn', [0,0,0])
        self.ligands = [('A', [0.1,0,0]),
                        ('B', [-0.1,0,0]),
                        ('C', [0,0.1,0]),
                        ('D', [0,-0.1,0]),
                        ('E', [0,0,0.1]),
                        ('F', [0,0,-0.1]),
                        ('G', [0,0,-0.1]),
                        ('H', [0,0,-0.1]),
                        ('I', [0,0,-0.1]),
                        ('J', [0,0,-0.1]),
                        ('K', [0,0,-0.1]),
                        ('L', [0,0,-0.1]),
                        ('M', [0,0,-0.1]),
                        ('N', [0,0,-0.1]),
                        ('O', [0,0,-0.1]),
                        ('P', [0,0,-0.1])]
        self.ligtypes = ['Mn', 'A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P']
        self.poly = polyhedron.Polyhedron(self.centre, self.ligands, atomdict=None, ligtypes = self.ligtypes)

    def test_pointcolours(self):
        self.assertEqual(self.poly.pointcolours()[:7], ['b', 'r','g','c','m','y','k', 0.1, 0.2, float(0.3), 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0][:7])
        np.testing.assert_almost_equal(self.poly.pointcolours()[7:], [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
  
    

if __name__ == "__main__":

    test_classes_to_run = [ EmptyCentreDictInit,
                            EmptyCentreListInit,
                            EmptyCentreStringInit,
                            InitFromDictsLigTypeList,
                            InitFromDictsLigTypeDict,
                            InitFromStringsAtomDict,
                            SimpleOctahedronAsList,
                            SimpleOctahedronAsDict,
                            SimpleOctahedronAsAtomDict,
                            NoLigandsAsList,
                            NoLigandsAsDict,
                            NoLigandsAsAtomDict,
                            FullColourPalette
                           ]
    
    

    suites_list = []
    for test_class in test_classes_to_run:
        suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suites_list.append(suite)

    big_suite = unittest.TestSuite(suites_list)

    results = unittest.TextTestRunner().run(big_suite)