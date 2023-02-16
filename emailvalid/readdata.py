import numpy as np
from data_dct import data_dct
import pandas as pd
from scipy.linalg import eigh

def readdata(train = False,flag = 1,path=None,data=None):
   if train :
        file = pd.read_csv(path,engine='python')
        t = np.expand_dims(file.values[:, 3],axis=1)
        pre_s0 = np.expand_dims(file.values[:, 1],axis=1)
        fac_s0 = np.expand_dims(file.values[:, 2],axis=1)
   else:
        t = np.expand_dims(data[:, 3],axis=1)
        pre_s0 = np.expand_dims(data[:, 1],axis=1)
        fac_s0 = np.expand_dims(data[:, 2],axis=1)
   conc = np.concatenate([abs(pre_s0),abs(fac_s0)], axis=1)
   prefac = pca_row(conc)
   fac_s = prefac[:, 1]
   pre_s = prefac[:, 0]
   datafinal1 = data_dct(t, fac_s)
   datafinal2 = data_dct(t, pre_s)
   datafinal3 = datafinal2-datafinal1
   datafinal4 = (datafinal2+datafinal1)
   if flag==1:
         datafinal = np.concatenate([datafinal1/2, datafinal2/2, datafinal3, datafinal4],axis=1);
   else:
         datafinal = np.concatenate([datafinal1, datafinal2, datafinal3],axis=1);
   datafinal = abs(datafinal)
   return datafinal

def pca_row(X):
    meanValue = np.mean(X, 0)
    X = X - meanValue
    a = X.shape[0]-1
    b = X.shape[1]
    C = np.dot(X.T,X)/a+0.0000001*np.eye(b)
    w, v = eigh(C)
    order=np.argsort(-w)
    v=v[:,order]
    newx = np.dot(X, v)
    return newx
