import numpy as np



def pdf(m,v,x):
    d = np.prod(v)
    p = 0
    if d != 0:
       p = np.power(2 * np.pi * d,-0.5) * np.exp(np.dot(-0.5 * (x-m) / v,(x-m).T))
    return p

def mixture(mix,x):
    prob = 0
    for j in range(mix.M):
        m = mix.mean[j,:]
        v = mix.var[j,:]
        w = mix.weight[j]
        prob = prob + w*pdf(m,v,x)
    if prob == 0:
        prob = 2.2251e-308
    return prob

