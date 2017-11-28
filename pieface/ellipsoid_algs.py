import numpy as np
import logging
from choldate import cholupdate, choldowndate

log = logging.getLogger()


"""
 Algorithms to compute minimum bounding ellipsoid or a set of points.
 
 Minimum ellipsoid is defined as $(x-\bar(x))^T H (x-\bar(x)) \leq n$ where 
 $\bar(x)$ is the centre of the ellipsoid and $n$ is the dimension. 
 
 For an n-dimensional set of points, the minimum-volume ellipsoid can be calculated
 by finding the minimum volume n+1 dimensional ellipsoid, with origin at the centre (\bar(x) = 0).
 
The  ellipsoid volume can be found from:
$vol(\Epsilon(H, \bar(x))) = \frac{n^{n/2} \Omega_n}{\sqrt{det H}}$
where $\Omega_n$ is the volume of a ball of radius 1. The optimisation process is therefore to minimise:

$ f(H) = -lndet(H) $
subject to the constraint that $x_i^T H x_i \leq n$,
where lndet is defined as:
lndet(H) = { ln det H         if H is positive definite,
           { -infinity        otherwise.

or alternatively, maximise $lndet(X U X^T)$ subject to $e^tU = 1$ and $u \geq 0$, where X is the matrix whose
columns are $x_i$, and U is a square matrix with Lagrangian multipliers $u$ on the diagonal.

Focussing on the second problem (maximising g(u)), the derivatives of g(u) are:

$
\del g(u) = \omega(u) = (x_i^T H(u) x_i)_{i=1}^m
(\del^2 g(u))_{ij} = - (x_i^T H(u) x_j)^2, i,j = 1,...,m,
$
where $H(u) = (X U X^T)^{-1}$.

For further details and derivations, see Todd (2013); 'Minimum-Volume
Ellipsoids: Theory and Algorithms'.

"""

def khachiyan_orig(points, tolerance, maxcycles):
    """ Original ellipsoid minimisation routine"""
    
    (N, d) = np.shape(points)
    d = float(d)

    # Q will be our working array
    Q = np.vstack([np.copy(points.T), np.ones(N)]) 
    QT = Q.T
    # initialisations
    err = 1.0 + tolerance
    u = (1.0 / N) * np.ones(N)

    count=0

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
    #print "Converged with tolerance {0} in {1} iterations".format(loctol, count)
    
def direct_inversion(points, tolerance, maxcycles):
    """ Calculate minimum bounding ellipsoid through computing matrix inverse. """
    
    (N, d) = np.shape(points)
    d = float(d)

    # Q will be our working array
    Q = np.vstack([np.copy(points.T), np.ones(N)]) 
    QT = Q.T
    # initialisations
    err = 1.0 + tolerance
    
    u = initwght(Q, method='KY')
    #print u

    count=0

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
    #print "Converged with tolerance {0} in {1} iterations".format(loctol, count)

def original_modified(points, tolerance, maxcycles):
    """ Original ellipsoid minimisation routine"""
    
    (N, d) = np.shape(points)
    n = float(d + 1)

    # Q will be our working array
    X = np.vstack([np.copy(points.T), np.ones(N)]) 
    XT = X.T
    # initialisations
    err = 1.0 + tolerance
    u = (1.0 / N) * np.ones(N)

    count=0

    # Khachiyan Algorithm
    while err > tolerance:
        V = np.dot(X, np.dot(np.diag(u), XT))
        M = np.diag(np.dot(XT , np.dot(np.linalg.inv(V), X)))    # M the diagonal vector of an NxN matrix
        j = np.argmax(M)
        maximum = M[j]
        
        A = np.dot(np.diag(np.sqrt(u)), X.T)   # U^0.5X^T = QR, but XUX^T = R^TR
        Q, R = np.linalg.qr(A)
        RX = np.linalg.lstsq(R.T, X)[0]   # RX = R^{-T}.X
        var = np.multiply(RX, RX).sum(axis=0)
        #print var.max()
        
        step_size = (maximum - n) / ((n) * (maximum - 1.0))
        new_u = (1.0 - step_size) * u
        new_u[j] += step_size
        err = np.linalg.norm(new_u - u)
        
        if maxcycles != 0:
            if count > maxcycles-1:
                tolerance = err
                break
        u = new_u
        count += 1
        
    print "Converged with a maximum variance of {0}".format(var.max())
        
    return u
    #print "Converged with tolerance {0} in {1} iterations".format(loctol, count)
    
def FederovWynn(points, tolerance, maxcycles):
    """ Compute minimum ellipsoid using Federov-Wynn-Franke-Wolfe algorithm """
    
    (N, d) = np.shape(points)
    n = float(d+1)

    # X will be our working array
    # Additional dimension (=1) allows ellipsoid to be fit centred on origin
    X = np.vstack([np.copy(points.T), np.ones(N)]) 
    XT = X.T
    
    # initialise weights (Khachiyan)
    err = (1+tolerance)
    u = (1.0 / N) * np.ones(N)
    
    # Initialise Cholesky factor
    upos = np.where(u > 0)[0]
    lupos = len(upos)
    
    A = np.dot(np.diag(np.sqrt(u)), X.T)   # U^0.5X^T = QR, but XUX^T = R^TR
    
    Q, R = np.linalg.qr(A)
    
    factor = 1   # M = A^T.A = X.U.X^T, but M = factor^-1 * R^T . R^T
    
    # Initialise Variance
    RX = np.linalg.lstsq(R.T, X)[0]   # RX = R^{-T}.X
    var = np.multiply(RX, RX).sum(axis=0)
    
    
    maxj = var.argmax()
    maxvar = var[maxj]
    
    #ind = var[upos].argmin()
    #minvar = var[upos][ind]
    #minj = upos[ind]
    #mnvup = n
    
    iter = 0
    
    while maxvar > (1+tolerance)*n and (iter < maxcycles):
        #print maxvar, maxj
        #if maxvar + mnvup > 2*n:
        #    j = maxj
        #    mvar = maxvar
        #else:
        #    j = minj
        #    mvar = mnvup
            
        # Compute Mxj = M^{-1} x_j and recompute var_j
        flag_recompute = 0
        xj = X[:, maxj]
        Rxj = np.linalg.lstsq(R.T, xj)[0]
        Mxj = factor * np.linalg.lstsq(R, Rxj)[0]
        mvarn = factor * np.dot( Rxj.T, Rxj)
        mvarerror = np.abs(mvarn - maxvar) / np.max([1, maxvar])
        if mvarerror > tolerance:
            flag_recompute = 1
        maxvar = mvarn
        
        # Compute stepsize LAM, epsilon and improvement in LOGDET
        lam = (maxvar - n) / ((n-1)*maxvar)
        #ep = (maxvar / d - 1)
        #uj = u[j]
        #lam = np.max([lam, -uj])
        
        # Update u, making sure it stays non-negative
        #imp = np.log(1 + lam*mvar) - d * np.log(1 + lam)
        uold = u
        u[maxj] = np.max([u[maxj] + lam, 0])
        u = (1.0 / (1 + lam)) * u
        upos = np.where(u > tolerance)[0]
        
        
        
        # Update Cholesky factors
        if ((iter > 0) and iter % 50000 == 0 ) or flag_recompute == 1:
            #print iter
            upos = np.where(u>0)[0]
            lupos = len(upos)
            
            M = np.dot(X[:, upos], np.dot(np.diag(uold[upos]), X[:, upos].T))
            normdiff = np.linalg.norm(factor*M - np.dot(R.T, R)) / (factor * np.linalg.norm(M))
            if normdiff > tolerance:
                flag_recompute = 1
            
        if flag_recompute:
            upos = np.where(u>0)[0]
            lupos = len(upos)
            
            A = np.dot(np.diag(np.sqrt(u)), X.T)  
            Q, R = np.linalg.qr(A)
            factor = 1
            RX = np.linalg.lstsq(R.T, X)[0]   # RX = R^{-T}.X
            var = np.multiply(RX, RX).sum(axis=0)
        
        else:
            # Update factorisations
            R, factor = updateR(R, factor, xj, lam)
                
            mult= lam / (1.0 + lam*maxvar)
            var = updatevar(var, lam, mult, Mxj, X)
                
        # Update maxvar
        maxj = np.argmax(var)
        maxvar = var[maxj]
        
        # Update minvar
        upos = np.where(u>0)[0]
        #ind = np.argmin(var[upos])
        #minvar = var[upos][ind]
        #minj = upos[ind]
        #mnvup = minvar
            
        iter += 1
            
    print "Converged in {0} iterations".format(iter - 1)
    
    return u

    
def WolfeAtwood(points, tolerance, maxcycles):
    """ Compute minimum ellipsoid using Wolfe algorithm """
    
    raise NotImplementedError
    
    (N, d) = np.shape(points)
    d = float(d)

    # X will be our working array
    # Additional dimension (=1) allows ellipsoid to be fit centred on origin
    X = np.vstack([np.copy(points.T), np.ones(N)]) 
    XT = X.T
    
    # initialise weights (Khachiyan)
    err = 1.0 + tolerance
    u = (1.0 / N) * np.ones(N)
    
    # Initialise Cholesky factor
    upos = np.where(u > 0)[0]
    lupos = len(upos)
    
    A = np.dot(np.diag(np.sqrt(u)), X.T)   # U^0.5X^T = QR, but XUX^T = R^TR
    
    Q, R = np.linalg.qr(A)
    
    factor = 1   # M = A^T.A = X.U.X^T, but M = factor^-1 * R^T . R^T
    
    # Initialise Variance
    RX = np.linalg.lstsq(R.T, X)[0]   # RX = R^{-T}.X
    var = np.multiply(RX, RX).sum(axis=0)
    
    
    maxj = var.argmax()
    maxvar = var[maxj]
    
    ind = var[upos].argmin()
    minvar = var[upos][ind]
    minj = upos[ind]
    mnvup = minvar
    
    iter = 0
    
    while maxvar > tolerance and (iter < maxcycles):
        if maxvar + mnvup > 2*d:
            j = maxj
            mvar = maxvar
        else:
            j = minj
            mvar = mnvup
            
        # Compute Mxj = M^{-1} x_j and recompute var_j
        flag_recompute = 0
        xj = X[:, j]
        Rxj = np.linalg.lstsq(R.T, xj)[0]
        Mxj = factor * np.linalg.lstsq(R, Rxj)[0]
        mvarn = factor * np.dot( Rxj.T, Rxj)
        mvarerror = np.abs(mvarn - mvar) / np.max([1, mvar])
        if mvarerror > tolerance:
            flag_recompute = 1
        mvar = mvarn
        
        # Compute stepsize LAM, epsilon and improvement in LOGDET
        lam = (mvar - d) / ((d-1)*mvar)
        ep = (mvar / d - 1)
        uj = u[j]
        lam = np.max([lam, -uj])
        
        # Update u, making sure it stays non-negative
        imp = np.log(1 + lam*mvar) - d * np.log(1 + lam)
        uold = u
        u[j] = np.max([u[j] + lam, 0])
        u = (1.0 / (1 + lam)) * u
        upos = np.where(u > tolerance)[0]
        
        
        # Update Cholesky factors
        if ((iter > 0) and iter % 50000 == 0 ) or flag_recompute:
            upos = np.where(u>0)[0]
            lupos = len(upos)
            
            M = np.dot(X[:, upos], np.dot(np.diag(uold[upos]), X[:, upos].T))
            normdiff = np.linalg.norm(factor*M - np.dot(R.T, R)) / (factor * np.linalg.norm(M))
            if normdiff > tolerance:
                flag_recompute = 1
            
            if flag_recompute:
                upos = np.where(u>0)[0]
                lupos = len(upos)
                
                A = np.dot(np.diag(np.sqrt(u)), X.T)  
                Q, R = np.linalg.qr(A)
                factor = 1
                RX = np.linalg.lstsq(R.T, X)[0]   # RX = R^{-T}.X
                var = np.multiply(RX, RX).sum(axis=0)
            
            else:
                # Update factorisations
                R, factor = updateR(R, factor, xj, lam)
                    
                mult= lam / (1.0 + lam*mvar)
                var = updatevar(var, lam, mult, Mxj, X)
                
            # Update maxvar
            maxj = np.argmax(var)
            maxvar = var[maxj]
            
            # Update minvar
            upos = np.where(u>0)[0]
            ind = np.argmin(var[upos])
            minvar = var[upos][ind]
            minj = upos[ind]
            mnvup = minvar
            
        iter += 1
            
    return u
            
def updatevar(var, lam, mult, Mxj, X):
    """ Update variances \omega_i(u) after rank-one update """
    tmp = np.dot(Mxj.T, X)
    var = (1.0 + lam) * (var - mult * (tmp**2))
    return var
                
def updateR(R, factor, xj, lam):
    """ Update Cholesky R factors after rank-one update. """

    xx = np.sqrt(np.abs(lam)*factor)*xj
    if lam > 0:
        cholupdate(R, xx)
    else:
        choldowndate(R, xx)
        
    factor = factor * (1 + lam)
    
    return R, factor
    
def initwght(X, method='K'):
    """ Find initial weights for ellipsoid fit.
    
    Parameters
    -----------
    X : np.ndarray
             n*m array, representing n-coordinates of m-points

    method : string
            Method to initialise weights: Khachiyan [K] (equal weights) or 
            Kumar-Yildirim [KY]
            
    returns
    -------
    weights : np.array  
            Array of length m, containing initial weights
    """
    
    if method.upper() == 'K' or method.upper() == 'KHACHIYAN':
        n,m = X.shape
        u = (1.0 / m) * np.ones(m)
        return u
        
    elif method.upper() == 'KY' or method.upper() == 'KUMAR-YILDIRIM' or method.upper() == 'KUMARYILDIRIM':
    
        n,m = X.shape
        
        u = np.zeros((m))
        Q = np.eye(n)
        d = Q[:, 0]
        
        # Q is an orthogonal matrix whose first j columns space the same space as
        # the first j points chosen
        
        for j in range(n):
            dX = np.abs( np.dot(d.T, X) )
            ind = dX.argmax()
            maxdX = dX[ind]
            u[ind] = 1
            if j == (n-1):
                break
            
            # Update Q
            y = X[:, ind]
            z = np.dot(Q.T, y)
            
            if j > 0:
                z[:j] = np.zeros(j)
            
            zeta = np.linalg.norm(z)
            zj = z[j]
            if z[j] < 0:
                zeta = -zeta
                
            zj = zj + zeta
            z[j] = zj
            Q = Q - (np.dot(Q, z)) * (np.dot( 1.0/(zeta*zj), z.T))
            d = Q[:, j+1]
            
        return u/m
        
            
    else:
        raise ValueError('Unknown method to calculate initial weights')
    
    
    
    
    
    
    
    
    
    
    
    
    
    
##############
## Testing benchmarks:

#### points = np.array([[0,0.5,1],[0,0,-2],[0.1,0.8,2],[-0.4,-1,0],[1,0,0.2],[-1,0,0.2]])


### Original Khachiyan algorithm                         : 23.2 s
### Original algortihm with variance calculation         : 2min 3s
### Direct inversion with K initialisation (as orig)     : 24.1 s
### Direct inversion with KY initialisation              : 23.9 s
### FederovWynn with equal weights                       : 6 mins


# Output from cProfile.run:

#########################################################
################### Original algorithm ##################
#########################################################

         # 39503328 function calls in 32.082 seconds

   # Ordered by: standard name

   # ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        # 1    0.000    0.000   32.082   32.082 <string>:1(<module>)
        # 1    6.235    6.235   32.082   32.082 ellipsoid_algs.py:43(khachiyan_orig)
   # 790066    0.684    0.000    1.578    0.000 fromnumeric.py:1201(diagonal)
        # 1    0.000    0.000    0.000    0.000 fromnumeric.py:1568(shape)
   # 790066    0.295    0.000    1.265    0.000 fromnumeric.py:911(argmax)
        # 1    0.000    0.000    0.000    0.000 function_base.py:894(copy)
   # 790066    0.472    0.000    0.472    0.000 linalg.py:101(get_linalg_error_extobj)
   # 790066    0.504    0.000    0.978    0.000 linalg.py:106(_makearray)
  # 2370198    0.564    0.000    0.917    0.000 linalg.py:111(isComplexType)
   # 790066    0.250    0.000    0.330    0.000 linalg.py:124(_realType)
   # 790066    1.114    0.000    1.879    0.000 linalg.py:139(_commonType)
   # 790066    1.962    0.000    3.839    0.000 linalg.py:1976(norm)
   # 790066    0.400    0.000    0.444    0.000 linalg.py:198(_assertRankAtLeast2)
   # 790066    0.662    0.000    0.989    0.000 linalg.py:209(_assertNdSquareness)
   # 790066    6.412    0.000   12.221    0.000 linalg.py:458(inv)
        # 2    0.000    0.000    0.000    0.000 numeric.py:141(ones)
  # 1580132    0.620    0.000    0.784    0.000 numeric.py:406(asarray)
  # 2370200    0.885    0.000    1.103    0.000 numeric.py:476(asanyarray)
        # 1    0.000    0.000    0.000    0.000 shape_base.py:180(vstack)
        # 2    0.000    0.000    0.000    0.000 shape_base.py:61(atleast_2d)
  # 1580132    2.914    0.000    5.945    0.000 twodim_base.py:244(diag)
   # 790066    0.072    0.000    0.072    0.000 {abs}
   # 790066    0.107    0.000    0.107    0.000 {getattr}
   # 790066    0.293    0.000    0.293    0.000 {isinstance}
  # 3160264    0.502    0.000    0.502    0.000 {issubclass}
  # 3160270    0.201    0.000    0.201    0.000 {len}
   # 790066    0.209    0.000    0.209    0.000 {max}
   # 790066    0.080    0.000    0.080    0.000 {method '__array_prepare__' of 'numpy.ndarray' objects}
        # 2    0.000    0.000    0.000    0.000 {method 'append' of 'list' objects}
   # 790066    0.970    0.000    0.970    0.000 {method 'argmax' of 'numpy.ndarray' objects}
   # 790066    0.693    0.000    0.693    0.000 {method 'astype' of 'numpy.ndarray' objects}
   # 790066    0.258    0.000    0.258    0.000 {method 'diagonal' of 'numpy.ndarray' objects}
        # 1    0.000    0.000    0.000    0.000 {method 'disable' of '_lsprof.Profiler' objects}
   # 790066    0.081    0.000    0.081    0.000 {method 'get' of 'dict' objects}
   # 790066    0.385    0.000    0.385    0.000 {method 'ravel' of 'numpy.ndarray' objects}
   # 790066    0.118    0.000    0.118    0.000 {min}
  # 3950333    0.382    0.000    0.382    0.000 {numpy.core.multiarray.array}
        # 1    0.000    0.000    0.000    0.000 {numpy.core.multiarray.concatenate}
        # 2    0.000    0.000    0.000    0.000 {numpy.core.multiarray.copyto}
  # 3950330    3.292    0.000    3.292    0.000 {numpy.core.multiarray.dot}
        # 2    0.000    0.000    0.000    0.000 {numpy.core.multiarray.empty}
   # 790066    0.463    0.000    0.463    0.000 {numpy.core.multiarray.zeros}

############################################################################
################### Direct inversion (with equal weights) ##################
############################################################################

         # 39503330 function calls in 31.919 seconds

   # Ordered by: standard name

   # ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        # 1    0.000    0.000   31.919   31.919 <string>:1(<module>)
        # 1    0.000    0.000    0.000    0.000 ellipsoid_algs.py:419(initwght)
        # 1    6.155    6.155   31.919   31.919 ellipsoid_algs.py:79(direct_inversion)
   # 790066    0.663    0.000    1.546    0.000 fromnumeric.py:1201(diagonal)
        # 1    0.000    0.000    0.000    0.000 fromnumeric.py:1568(shape)
   # 790066    0.294    0.000    1.265    0.000 fromnumeric.py:911(argmax)
        # 1    0.000    0.000    0.000    0.000 function_base.py:894(copy)
   # 790066    0.480    0.000    0.480    0.000 linalg.py:101(get_linalg_error_extobj)
   # 790066    0.496    0.000    0.966    0.000 linalg.py:106(_makearray)
  # 2370198    0.558    0.000    0.909    0.000 linalg.py:111(isComplexType)
   # 790066    0.241    0.000    0.321    0.000 linalg.py:124(_realType)
   # 790066    1.116    0.000    1.871    0.000 linalg.py:139(_commonType)
   # 790066    1.942    0.000    3.797    0.000 linalg.py:1976(norm)
   # 790066    0.415    0.000    0.458    0.000 linalg.py:198(_assertRankAtLeast2)
   # 790066    0.662    0.000    0.988    0.000 linalg.py:209(_assertNdSquareness)
   # 790066    6.423    0.000   12.229    0.000 linalg.py:458(inv)
        # 2    0.000    0.000    0.000    0.000 numeric.py:141(ones)
  # 1580132    0.615    0.000    0.778    0.000 numeric.py:406(asarray)
  # 2370200    0.883    0.000    1.101    0.000 numeric.py:476(asanyarray)
        # 1    0.000    0.000    0.000    0.000 shape_base.py:180(vstack)
        # 2    0.000    0.000    0.000    0.000 shape_base.py:61(atleast_2d)
  # 1580132    2.893    0.000    5.885    0.000 twodim_base.py:244(diag)
   # 790066    0.071    0.000    0.071    0.000 {abs}
   # 790066    0.108    0.000    0.108    0.000 {getattr}
   # 790066    0.284    0.000    0.284    0.000 {isinstance}
  # 3160264    0.504    0.000    0.504    0.000 {issubclass}
  # 3160270    0.200    0.000    0.200    0.000 {len}
   # 790066    0.209    0.000    0.209    0.000 {max}
   # 790066    0.081    0.000    0.081    0.000 {method '__array_prepare__' of 'numpy.ndarray' objects}
        # 2    0.000    0.000    0.000    0.000 {method 'append' of 'list' objects}
   # 790066    0.971    0.000    0.971    0.000 {method 'argmax' of 'numpy.ndarray' objects}
   # 790066    0.691    0.000    0.691    0.000 {method 'astype' of 'numpy.ndarray' objects}
   # 790066    0.258    0.000    0.258    0.000 {method 'diagonal' of 'numpy.ndarray' objects}
        # 1    0.000    0.000    0.000    0.000 {method 'disable' of '_lsprof.Profiler' objects}
   # 790066    0.080    0.000    0.080    0.000 {method 'get' of 'dict' objects}
   # 790066    0.382    0.000    0.382    0.000 {method 'ravel' of 'numpy.ndarray' objects}
        # 1    0.000    0.000    0.000    0.000 {method 'upper' of 'str' objects}
   # 790066    0.117    0.000    0.117    0.000 {min}
  # 3950333    0.380    0.000    0.380    0.000 {numpy.core.multiarray.array}
        # 1    0.000    0.000    0.000    0.000 {numpy.core.multiarray.concatenate}
        # 2    0.000    0.000    0.000    0.000 {numpy.core.multiarray.copyto}
  # 3950330    3.289    0.000    3.289    0.000 {numpy.core.multiarray.dot}
        # 2    0.000    0.000    0.000    0.000 {numpy.core.multiarray.empty}
   # 790066    0.460    0.000    0.460    0.000 {numpy.core.multiarray.zeros}

############################################################################
################### Direct inversion (with KY weights) #####################
############################################################################

         # 39320023 function calls in 31.996 seconds

   # Ordered by: standard name

   # ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        # 1    0.000    0.000   31.996   31.996 <string>:1(<module>)
        # 1    0.000    0.000    0.001    0.001 ellipsoid_algs.py:419(initwght)
        # 1    6.203    6.203   31.996   31.996 ellipsoid_algs.py:79(direct_inversion)
   # 786399    0.664    0.000    1.543    0.000 fromnumeric.py:1201(diagonal)
        # 1    0.000    0.000    0.000    0.000 fromnumeric.py:1568(shape)
   # 786399    0.295    0.000    1.267    0.000 fromnumeric.py:911(argmax)
        # 1    0.000    0.000    0.000    0.000 function_base.py:894(copy)
   # 786399    0.477    0.000    0.477    0.000 linalg.py:101(get_linalg_error_extobj)
   # 786399    0.495    0.000    0.966    0.000 linalg.py:106(_makearray)
  # 2359200    0.552    0.000    0.906    0.000 linalg.py:111(isComplexType)
   # 786399    0.243    0.000    0.322    0.000 linalg.py:124(_realType)
   # 786399    1.104    0.000    1.858    0.000 linalg.py:139(_commonType)
   # 786402    1.984    0.000    3.843    0.000 linalg.py:1976(norm)
   # 786399    0.400    0.000    0.444    0.000 linalg.py:198(_assertRankAtLeast2)
   # 786399    0.661    0.000    0.985    0.000 linalg.py:209(_assertNdSquareness)
   # 786399    6.415    0.000   12.182    0.000 linalg.py:458(inv)
        # 1    0.000    0.000    0.000    0.000 numeric.py:141(ones)
  # 1572801    0.618    0.000    0.782    0.000 numeric.py:406(asarray)
  # 2359199    0.878    0.000    1.095    0.000 numeric.py:476(asanyarray)
        # 1    0.000    0.000    0.000    0.000 shape_base.py:180(vstack)
        # 2    0.000    0.000    0.000    0.000 shape_base.py:61(atleast_2d)
        # 1    0.000    0.000    0.000    0.000 twodim_base.py:192(eye)
  # 1572798    2.905    0.000    5.900    0.000 twodim_base.py:244(diag)
   # 786399    0.072    0.000    0.072    0.000 {abs}
   # 786399    0.108    0.000    0.108    0.000 {getattr}
   # 786399    0.284    0.000    0.284    0.000 {isinstance}
  # 3145599    0.506    0.000    0.506    0.000 {issubclass}
  # 3145602    0.200    0.000    0.200    0.000 {len}
   # 786399    0.208    0.000    0.208    0.000 {max}
   # 786399    0.081    0.000    0.081    0.000 {method '__array_prepare__' of 'numpy.ndarray' objects}
        # 2    0.000    0.000    0.000    0.000 {method 'append' of 'list' objects}
   # 786403    0.972    0.000    0.972    0.000 {method 'argmax' of 'numpy.ndarray' objects}
   # 786399    0.684    0.000    0.684    0.000 {method 'astype' of 'numpy.ndarray' objects}
   # 786399    0.257    0.000    0.257    0.000 {method 'diagonal' of 'numpy.ndarray' objects}
        # 1    0.000    0.000    0.000    0.000 {method 'disable' of '_lsprof.Profiler' objects}
   # 786399    0.079    0.000    0.079    0.000 {method 'get' of 'dict' objects}
   # 786402    0.377    0.000    0.377    0.000 {method 'ravel' of 'numpy.ndarray' objects}
        # 3    0.000    0.000    0.000    0.000 {method 'upper' of 'str' objects}
   # 786399    0.116    0.000    0.116    0.000 {min}
  # 3932001    0.381    0.000    0.381    0.000 {numpy.core.multiarray.array}
        # 1    0.000    0.000    0.000    0.000 {numpy.core.multiarray.concatenate}
        # 1    0.000    0.000    0.000    0.000 {numpy.core.multiarray.copyto}
  # 3932011    3.308    0.000    3.308    0.000 {numpy.core.multiarray.dot}
        # 1    0.000    0.000    0.000    0.000 {numpy.core.multiarray.empty}
   # 786403    0.467    0.000    0.467    0.000 {numpy.core.multiarray.zeros}
        # 1    0.000    0.000    0.000    0.000 {range}




