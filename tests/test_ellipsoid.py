""" Tests for ellipsoid.py """
import unittest
from pieface import ellipsoid
import numpy as np

class AllEllipsoidFunctions(object):
    """ Class to hold all tests, run by separate class holding data and values """
    @classmethod
    def setUpClass(cls):
        """ Initialise ellipsoid object and find minimum ellipsoid once per class, to speed things up """
        # Assumes that findellipsoid works as expected with supplied input!
        if cls.points is not None:
            cls.ellipob = ellipsoid.Ellipsoid(points = cls.points, tolerance=cls.tolerance)
            cls.ellipob.findellipsoid()
        else:
            cls.ellipob = ellipsoid.Ellipsoid(points = cls.points, tolerance=cls.tolerance)
    @classmethod
    def tearDownClass(cls):
        del(cls.ellipob)
        
    # def setUp(self):
        # """Initialise empty ellipsoid object and find ellipsoid (assumes findellipsoid() is ok)."""
        # self.ellipob = ellipsoid.Ellipsoid(points = self.points, tolerance=self.tolerance)
        # self.ellipob.findellipsoid()
    # def tearDown(self):
        # """ Delete ellipsoid object. """
        # del(self.ellipob)
        
    # Check attributes for correct value
    def test_centre(self):
        if self.valid['centre'] is not None:
            np.testing.assert_array_almost_equal(self.ellipob.centre, self.valid['centre'])
        else:
            self.assertTrue(self.ellipob.centre is None)
    def test_ellipdims(self):
        if self.valid['ellipdims'] is not None:
            self.assertEqual(self.ellipob.ellipdims,  self.valid['ellipdims'])
        else:
            self.assertTrue(self.ellipob.ellipdims is None)
    def test_numpoints(self):
        if self.valid['numpoints'] is not None:
            self.assertEqual(self.ellipob.numpoints(), self.valid['numpoints'])
        else:
            self.assertTrue(self.ellipob.numpoints is None)
    def test_radii(self):
        if self.valid['radii'] is not None:
            np.testing.assert_array_almost_equal(self.ellipob.radii, self.valid['radii'])
        else:
            self.assertTrue(self.ellipob.radii is None)
    def test_rotation(self):
        if self.valid['rotation'] is not None:
            np.testing.assert_array_almost_equal(self.ellipob.rotation, self.valid['rotation'])
        else:
            self.assertTrue(self.ellipob.rotation is None)
        
    # Check methods
    def test_ellipsvol(self):
        if self.valid['ellipsvol'] is not None:
            self.assertAlmostEqual(self.ellipob.ellipsvol(), self.valid['ellipsvol'])
        else:
            self.assertRaises(AttributeError, self.ellipob.ellipsvol)
    def test_meanrad(self):
        if self.valid['meanrad'] is not None:
            self.assertAlmostEqual(self.ellipob.meanrad(), self.valid['meanrad'])
        else:
            self.assertRaises(AttributeError, self.ellipob.meanrad)
    def test_radvar(self):
        if self.valid['radvar'] is not None:
            self.assertAlmostEqual(self.ellipob.radvar(), self.valid['radvar'])
        else:
            self.assertRaises(AttributeError, self.ellipob.raderr)
    def test_raderr(self):
        if self.valid['raderr'] is not None:
            self.assertAlmostEqual(self.ellipob.raderr(), self.valid['raderr'])
        else:
            self.assertRaises(AttributeError, self.ellipob.raderr)
    def test_shapeparam(self):
        if self.valid['shapeparam'] is not None:
            np.testing.assert_almost_equal(self.ellipob.shapeparam(), self.valid['shapeparam'])     # use np testing to deal with NaN (from zero division errors)
        else:
            self.assertRaises(AttributeError, self.ellipob.shapeparam)
    def test_sphererad(self):
        if self.valid['sphererad'] is not None:
            self.assertAlmostEqual(self.ellipob.sphererad(), self.valid['sphererad'])
        else:
            self.assertRaises(AttributeError, self.ellipob.sphererad)
    def test_strainenergy(self):
        if self.valid['strainenergy'] is not None:
            np.testing.assert_almost_equal(self.ellipob.strainenergy(), self.valid['strainenergy'])
        else:
            self.assertRaises(AttributeError, self.ellipob.strainenergy)
    def test_uniquerad(self):
        if self.valid['uniquerad'] is not None:
            self.assertEqual(self.ellipob.uniquerad(), self.valid['uniquerad'])
        else:
            self.assertRaises(AttributeError, self.ellipob.uniquerad)
    def test_tolerance_type(self):
        self.assertTrue( isinstance(self.ellipob.tolerance, float) or isinstance(self.ellipob.tolerance, np.float) )
    def check_tolerance_val(self):
        if self.tolerance is not None:
            self.assertAlmostEqual(self.ellipob.tolerance, self.valid['tolerance'])
    #def test_points(self):
    #    if self.points is not None:
    #        np.testing.assert_array_almost_equal(self.ellipob.points, self.points)
    #    else:
    #        self.assertRaises(AttributeError, getattr, self.ellipob, "points")       # points is not callable, so have to work around that with getattr
            
            
    # def test_findellipsoid(self):
        # self.assertRaises(AttributeError, self.ellipob.findellipsoid)
    # def test_getminvol(self):
        # self.assertRaises(AttributeError, self.ellipob.getminvol)
   

    
class SimpleOctEllipsoid(AllEllipsoidFunctions, unittest.TestCase):    
    """ Simple octahedron centred at origin, unit dimensions """
    points = np.array([[1,0,0],[-1,0,0],[0,1,0],[0,-1,0],[0,0,1],[0,0,-1]])

    valid = {'centre'       : np.array([0.,0.,0.]),
             'ellipdims'    : 3,
             'numpoints'    : 6,
             'radii'        : np.array([1.,1.,1.]),
             'rotation'     : np.array([[ 0.,  0.,  1.],\
                                        [ 0.,  1.,  0.],\
                                        [ 1.,  0.,  0.]]),
             'ellipsvol'    : float(4.1887902047863905),
             'meanrad'      : float(1.0),
             'radvar'       : float(0.0),
             'raderr'       : float(0.0),
             'shapeparam'   : float(0.0),
             'sphererad'    : float(1.0),
             'strainenergy' : float(0.0),
             'uniquerad'    : int(1)
             }
             
    tolerance = float(1.e-6)
    
    
class EmptyEllipsoidInit(AllEllipsoidFunctions, unittest.TestCase):
    """ Initialise empty ellipsoid to check init routines """
    points = None
    valid = {'centre'       : None,
             'ellipdims'    : None,
             'numpoints'    : None,
             'radii'        : None,
             'rotation'     : None,
             'ellipsvol'    : None,
             'meanrad'      : None,
             'radvar'       : None,
             'raderr'       : None,
             'shapeparam'   : None,
             'sphererad'    : None,
             'strainenergy' : None,
             'uniquerad'    : None
             }
    tolerance = float(1.e-6)    

class SinglePoint(AllEllipsoidFunctions, unittest.TestCase):
    """ Initialise single point to fit ellipsoid (offset from origin)"""
    points = np.array([[1.,1.,1.]])
    valid = {'centre'       : np.array([1.,1.,1.]),
             'ellipdims'    : 0,
             'numpoints'    : 1,
             'radii'        : np.zeros(3),
             'rotation'     : np.array([[ 1.,  0.,  0.],\
                                        [ 0.,  1.,  0.],\
                                        [ 0.,  0.,  1.]]),
             'ellipsvol'    : float(0.0),
             'meanrad'      : float(0.0),
             'radvar'       : float(0.0),
             'raderr'       : float(0.0),
             'shapeparam'   : np.nan,
             'sphererad'    : float(0.0),
             'strainenergy' : np.nan,
             'uniquerad'    : 0
             }
    tolerance = float(1.e-6) 
    
class LinearEllipse(AllEllipsoidFunctions, unittest.TestCase):
    """ Linear set of three points, centred at origin. """
    points = np.array([[0.,0.,0.],[1.,1.,1.],[-1.,-1.,-1.]])
    valid = {'centre'       : np.zeros(3),
             'ellipdims'    : 1,
             'numpoints'    : 3,
             'radii'        : np.array([np.sqrt(3.),0.,0.]),
             'rotation'     : np.array([[-0.57735 , -0.57735 , -0.57735 ],\
                                        [ 0.816497, -0.408248, -0.408248],\
                                        [-0.      ,  0.707107, -0.707107]]),
             'ellipsvol'    : float(0.0),
             'meanrad'      : np.sqrt(3) / 3.,
             'radvar'       : 2.0/3.0,
             'raderr'       : np.sqrt(2./3.),
             'shapeparam'   : np.nan,
             'sphererad'    : float(0.0),
             'strainenergy' : np.nan,
             'uniquerad'    : 1
             }
    tolerance = float(1.e-6)
    
class PlanarEllipse(AllEllipsoidFunctions, unittest.TestCase):
    """ Set of three points arranged in an equilateral triangle, rotated by 45 degrees in xy plane """
    points = np.array([[np.sqrt(6.),np.sqrt(6),0],[1,-1,0],[-1,1,0]])
    valid = {'centre'       : np.array([np.sqrt(6) / 3., np.sqrt(6) / 3., 0.]) ,
             'ellipdims'    : 2,
             'numpoints'    : 3,
             'radii'        : np.array([2.309401, 1.632993, 0.]),
             'rotation'     : np.array([[  np.sqrt(2)/2., np.sqrt(2)/2., 0. ],\
                                        [ -np.sqrt(2)/2., np.sqrt(2)/2., 0.],\
                                        [ 0.           ,  0.           , 1.]]),
             'ellipsvol'    : float(0.0),
             'meanrad'      : float(1.3141314128713184),
             'radvar'       : 0.93972529637149949,
             'raderr'       : np.sqrt(0.93972529637149949),
             'shapeparam'   : -np.sqrt(2)/2.0,
             'sphererad'    : float(0.0),
             'strainenergy' : np.nan,
             'uniquerad'    : 2
             }
    tolerance = float(1.e-6)


    
if __name__ == "__main__":

    test_classes_to_run = [SimpleOctEllipsoid,
                           EmptyEllipsoidInit,
                           SinglePoint,
                           LinearEllipse,
                           PlanarEllipse
                           ]
    
    

    suites_list = []
    for test_class in test_classes_to_run:
        suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suites_list.append(suite)

    big_suite = unittest.TestSuite(suites_list)

    results = unittest.TextTestRunner().run(big_suite)

    