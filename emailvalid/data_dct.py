import copy

import numpy as  np


def data_dct(times,SC):
    a = len(SC)
    H = dct(SC,a)
    J = H
    L = np.zeros([a,1])
    ds = 22
    K= 1 + (ds / 2) * np.sin(np.pi  / ds)
    for i in range(0,a):
        L[i]= J[i] * K
    feat = L
    dtfeat = np.zeros([a,1])
    for i in range(1, a ):
        dt = times[i] - times[i - 1]
        if ( dt == 0 ):
              if i == 1:
                    dtfeat[i - 1,:] =0
              else:
                    dtfeat[i - 1,:] = dtfeat[i - 2,:]
        else:
            dtfeat[i - 1,:] = (feat[i,:] - feat[i - 1,:]) / dt
    dtfeat = dtfeat / 2
    result = np.concatenate([feat[0:a-1,:],dtfeat[0:a-1,:]],axis=1)
    return result

def dct(x,a):
    y = copy.deepcopy(x)
    for k in range(a):
        data = 0
        if (k == 0) :
            ak=np.sqrt(1 / a)
        else :
            ak=np.sqrt(2.0 / a)
        for j in range (a):
             t = x[j] * np.cos(((2 * j+1) * k * np.pi) / (2 * a))
             data = data + t
        y[k]=ak * data
    return y
