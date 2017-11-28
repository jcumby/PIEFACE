import numpy as np
cimport numpy as np

DTYPE=np.float64

ctypedef np.float64_t DTYPE_t

def khachiyan_orig(np.ndarray[DTYPE_t, ndim=2] X, float tolerance, int maxcycles):
    """ Original ellipsoid minimisation routine"""
    
    cdef int N = X.shape[0]
    cdef float d = X.shape[1]
    
    cdef np.ndarray[DTYPE_t, ndim=2] Q = np.vstack([X.T, np.ones(N, dtype=DTYPE)]) 
    cdef np.ndarray[DTYPE_t, ndim=2] QT = Q.T
    cdef float err = 1.0 + tolerance
    cdef np.ndarray[DTYPE_t, ndim=1] u = (1.0 / N) * np.ones(N, dtype=DTYPE)
    
    cdef int count=0
    
    cdef np.ndarray[DTYPE_t, ndim=2] V
    cdef np.ndarray[DTYPE_t, ndim=1] M
    cdef np.ndarray[DTYPE_t, ndim=1] new_u
    cdef int j
    cdef float step_size

    
    
    # Khachiyan Algorithm
    while err > tolerance:
        V = np.dot(Q, np.dot(np.diag(u), QT))
        M = np.diag(np.dot(QT , np.dot(np.linalg.inv(V), Q)))    # M the diagonal vector of an NxN matrix
        j = np.argmax(M)
        maximum = M[j]
        step_size = (maximum - d - 1.0) / ((d + 1.0) * (maximum - 1.0))
        new_u = (1.0 - step_size) * u
        new_u[j] += step_size
        err = np.linalg.norm(new_u - u)
        
        if maxcycles != 0:
            if count > maxcycles-1:
                tolerance = err
                break
        u = new_u
        count += 1
        
    return u
        
        
# Timings:

# Original function (pure Python)         : 23.2 s
# Original python function  (cythonised)  : 23.8 s
# Function with type definitions          : 21.8 s
# With typed ndarray objects              : 24.7 s