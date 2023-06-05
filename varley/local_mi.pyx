#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May  4 22:18:28 2023

@author: thosvarley
"""

import cython
cimport cython

import numpy as np
cimport numpy as np 

from libc.math cimport log, exp, sqrt, pi, fmin
from cython.parallel import prange


cdef double _SQRT_2PI = sqrt(2.0*pi)
cdef double _2PI = 2.0*pi


@cython.wraparound(False)
@cython.initializedcheck(False)
@cython.cdivision(True)
@cython.boundscheck(False)
cdef double _mean(double[:] X):
    """
    Calculates the mean of a 1-dimensional array. 
    """
    cdef double total = 0.0
    cdef double N = X.shape[0]
    cdef int i 
    
    for i in prange(X.shape[0], nogil=True):
        total += X[i]
        
    return total / N


@cython.wraparound(False)
@cython.initializedcheck(False)
@cython.cdivision(True)
@cython.boundscheck(False)
cdef double _var(double[:] X):
    """
    Calculates the variance of a 1-dimensional array.
    """
    cdef double avg = _mean(X)
    cdef double total = 0.0
    cdef double N = X.shape[0]
    cdef int i 
    
    for i in prange(X.shape[0], nogil=True):
        total += (X[i] - avg)**2
    
    return total / N


@cython.wraparound(False)
@cython.initializedcheck(False)
@cython.cdivision(True)
@cython.boundscheck(False)
cdef double _std(double[:] X):
    """
    Calculates the standard deviation of a 1-dimensional array.
    """
    cdef double avg = _mean(X)
    cdef double total = 0.0
    cdef double N = X.shape[0]
    cdef int i 
    
    for i in prange(X.shape[0], nogil=True):
        total += (X[i] - avg)**2
    
    total /= N
    
    return sqrt(total)

@cython.initializedcheck(False)
@cython.cdivision(True)
cdef double _gaussian(double x, double mu, double sigma) nogil:
    """
    Calculates the probability density of a point pulled from a univariate Gaussian. 
    Arguments: 
        x: A floating point value: the instantanious value of the z-scored timeseries.
        mu: A floating point value: The mean of the distribution P(X).
        sigma: A floating point value: the standard deviation of the distribution P(X)
    """
    return 1.0 / (sigma * _SQRT_2PI) * exp(-0.5*((x-mu)/sigma)**2.0)


@cython.initializedcheck(False)
cdef double _local_entropy(double x, double mu, double sigma) nogil:
    """
    The shannon information content of a single variable.
    Essentially just a -log() wrapper for the _gaussian() function.
    Takes all the same arguments.
    """
    return -1.0*log(_gaussian(x, mu, sigma))


@cython.initializedcheck(False)
@cython.wraparound(False)
@cython.boundscheck(False)
@cython.cdivision(True)
cdef double _gaussian_nd(double[:] x, double[:] mu, double[:,:] cov, double[:,:] inv, double det):
    """
    Calculates the probability of an n-dimensional Gaussian.
    Requires pre-computing important values such as the mu, covariance matrix,
        inverse covariance matrix, and determinant of the covariance matrix.
    Arguments:
        x: An n-dimensional vector.
        mu: An n-dimensional vector, mu_i is the mean of the ith dimension.
        cov: The covariance matrix.
        inv: The inverse of the covariance matrix.
        det: The determinant of the covariance matrix.
    """
    cdef int N = x.shape[0]
    cdef double Nf = x.shape[0]
    cdef double norm = 1.0 / sqrt(((_2PI)**(Nf)) * det)
    cdef double[:] err = np.zeros(N)
    
    cdef int i
    
    for i in range(N):
        err[i] = x[i] - mu[i]
    
    cdef double mul = -0.5 * np.matmul(np.matmul(err, inv, dtype="double"), err, dtype="double")
    return norm * exp(mul)


@cython.initializedcheck(False)
@cython.wraparound(False)
@cython.boundscheck(False)
cdef double _local_entropy_nd(double[:] vec, double[:] mu, double[:,:] cov, double[:,:] inv, double det):
    return -1.0*log(_gaussian_nd(vec, mu, cov, inv, det))


@cython.initializedcheck(False)
@cython.wraparound(False)
@cython.boundscheck(False)
def local_entropy_series_nd(double[:,:] X):
    
    cdef int N0 = X.shape[0]
    cdef int N1 = X.shape[1]

    cdef int i, j 
    
    cdef double[:] ents = np.zeros(N1)
    
    cdef double[:] vec = np.zeros(N0)
    cdef double[:] mu = np.zeros(N0)
    cdef double[:] sigma = np.zeros(N0)
    
    cdef double[:,:] cov, inv 
    cdef double det

    for i in range(N0):
        mu[i] = _mean(X[i])
        
    if N0 == 1:
        sigma[i] =  _std(X[0])
        for i in range(N1):
            ents[i] = _local_entropy(X[0][i], mu[0], sigma[0])
    else:
        cov = np.cov(X, ddof=0.0).reshape((X.shape[0], X.shape[0]))
        inv = np.linalg.inv(cov)
        det = np.linalg.det(cov)
        
        for i in range(N1):
            ents[i] = _local_entropy_nd(X[:,i], mu, cov, inv, det)
    
    return np.array(ents)

@cython.wraparound(False)
@cython.initializedcheck(False)
@cython.boundscheck(False)
@cython.cdivision(True)
def local_total_correlation(double[:,:] X):
    """
    Returns the local total correlation (integration) for every column in a muldimensional
    timeseries X. 
    
    If X.shape[0] == 2, returns the local mutual information (analagous to an edge time series.)
    """
    cdef int N0 = X.shape[0]
    cdef int N1 = X.shape[1]
    
    cdef double[:] mu = np.mean(X, axis=1)   
    cdef double[:] sigma = np.var(X, axis=1)
    
    cdef int i, j
    cdef double[:] joint_ents = local_entropy_series_nd(X)
    cdef double[:] sum_marg_ents = np.zeros(N1)
    cdef double mul
    
    for i in range(N1):
        for j in range(N0):
            sum_marg_ents[i] += _local_entropy(X[j,i], mu[j], sigma[j])
        
    return np.subtract(sum_marg_ents, joint_ents)

@cython.wraparound(False)
@cython.initializedcheck(False)
@cython.boundscheck(False)
@cython.cdivision(True)
def local_total_correlation_v2(double[:] x, double[:] y):
    """
    Returns the local total correlation (integration) for every column in a muldimensional
    timeseries X. 
    
    If X.shape[0] == 2, returns the local mutual information (analagous to an edge time series.)
    """
    cdef X = np.vstack((x, y))
    cdef int N0 = X.shape[0]
    cdef int N1 = X.shape[1]
    
    cdef double[:] mu = np.mean(X, axis=1)   
    cdef double[:] sigma = np.var(X, axis=1)
    
    cdef int i, j
    cdef double[:] joint_ents = local_entropy_series_nd(X)
    cdef double[:] sum_marg_ents = np.zeros(N1)
    cdef double mul
    
    for i in range(N1):
        for j in range(N0):
            sum_marg_ents[i] += _local_entropy(X[j,i], mu[j], sigma[j])
        
    return np.subtract(sum_marg_ents, joint_ents)

"""
#UNIT TEST FOR TC

from scipy.stats import zscore, pearsonr
data = zscore(np.random.randn(2, 10_000), axis=-1)

cov = np.cov(data, ddof=0.0)
det = np.linalg.det(cov)

exp_tc = -np.log(det)/2.0

print(
      np.isclose(
          local_total_correlation(data).mean(),
          exp_tc
          )
      )

#UNIT TEST FOR BIVARIATE MI 

r = pearsonr(data[0], data[1])[0]

mi = -np.log(1-(r**2))/2.0

print(
      np.isclose(
          local_total_correlation(data).mean(),
          mi
          )
      )

"""