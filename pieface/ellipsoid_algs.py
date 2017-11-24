import numpy as np


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
    
def WolfeAtwood(points, tolerance, maxcycles):
    """ Compute minimum ellipsoid using Wolfe algorithm """
    
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
    upos = np.where(u > 0)
    lupos = len(upos)
    
    A = np.dot(np.diag(np.sqrt(u)), X.T)   # U^0.5X^T = QR, but XUX^T = R^TR
    
    Q, R = np.linalg.qr(A)
    
    factor = 1   # M = A^T.A = X.U.X^T, but M = factor^-1 * R^T . R^T
    
    # Initialise Variance
    RX = np.linalg.lstsq(R.T, X)   # RX = R^{-T}.X
    var = np.multiply(RX, RX).sum(axis=0)
    
    
    maxj = var.argmin()
    maxvar = var[maxj]
    
    ind = var[upos].argmin()
    minvar = var[pos][ind]
    minj = upos[ind]
    mnvup = minvar
    
    while maxvar > tolerance:
        if maxvar + mnvup > 2*d:
            j = maxj
            mvar = maxvar
        else:
            j = minj
            mvar = mnvup
            
        # Compute Mxj = M^{-1} x_j and recompute var_j
        flag_recompute = 0
        xj = X[:, j]
        Rxj = np.linalg.lstsq(R.T, xj)
        Mxj = factor * np.linalg.lstsq(R, Rxj)
        mvarn = factor * np.dot( Rxj.T, Rxj)
        mvarerror = np.abs(mvarn - mvar) / np.max([1, mvar])
        if mvarerror > tolerance:
            flag_recompute = 1
        mvar = mvarn
        
        # Compute stepsize LAM, epsilon and improvement in LOGDET
        lam = (mvar - d) / ((d-1)*mvar)
        ep = (mvar / d - 1)
        uj = u[j]
        lam = np.max([lam, -uj]
        
        # Update u, making sure it stays non-negative
        imp = np.log(1 + lam*mvar) - d * np.log(1 + lam)
        uold = u
        u[j] = np.max([u[j] + lam, 0])
        u = (1.0 / (1 + lam)) * u
        upos = np.where(u > tolerance)
        
        
        
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
##############
## Testing benchmarks:

#### points = np.array([[0,0.5,1],[0,0,-2],[0.1,0.8,2],[-0.4,-1,0],[1,0,0.2],[-1,0,0.2]])


### Original Khachiyan algorithm: 23.2 s
