import numpy as np
import copy
from  mixture import mixture

def viterbi(hmmdata,O):
    hmm = copy.deepcopy(hmmdata)
    init = hmm.init
    trans = hmm.trans
    mix = hmm.mix
    N = hmm.N
    T = O.shape[0]
    # 计算log(init);
    for i, x in enumerate(init) :
        if x > 0:
            init[i] = np.log(init[i])
        elif x <= 0:
            init[i] = -np.inf
    for i, data in enumerate(trans) :
        for j, x in enumerate(data):
            if x > 0:
                trans[i,j] = np.log(trans[i,j])
            elif x <= 0:
                trans[i,j] = -np.inf
    deta = np.zeros([T,N])
    x=O[0,:]
    for i in range(N):
        deta[0,i] = init[i] + np.log(mixture(mix[i],x))
    for t in range(1,T):
        for j in range(N):
            deta[t,j] = max(deta[t-1,:] + trans[:,j].T)
            x = O[t,:]
            deta[t,j] = deta[t,j] + np.log(mixture(mix[j],x))
    prob = max(deta[T-1,:])
    return prob



