import numpy as np
import os
from readdata import readdata
from viterbi import viterbi
import scipy.io as scio
import operator
import json
import copy
import requests as rq
import time
from os import getenv
from pathlib import Path

BASE_URL = getenv("BASE_URL") or "http://localhost:8000"


class mix:
    def __init__(self):
        self.M = ""
        self.mean = ""
        self.var = ""
        self.weight = ""


class hmmstruct:
    def __init__(self):
        self.N = 4
        self.M = ""
        self.init = ""
        self.trans = ""
        self.mix = []
        if self.N > 0:
            for i in range(self.N):
                self.mix.append(mix())


def texttonumpy(data0):
    data = copy.deepcopy(data0)
    data = data['currentRecords']
    data = data.split("\n")
    matrix = []
    for i in range(1, len(data)):
        p0 = data[i].split(",")
        p = [np.float64(x) for x in p0]
        matrix.append(p)
    return [data0["sclassName"], data0["type"], "第{}档".format(data0["level"] + 1), np.array(matrix), data0["_id"]]


def load_hmmmode(match="NBA", model="增量", level="第1档"):
    # curpath = os.path.abspath(os.path.join(os.getcwd()))
    pack = Path("pack")
    modelpath = pack / match / model / level
    print(modelpath, "modal")
    # modelpath = "\\pack\\" + match + "\\" + model + "\\" + level
    print(modelpath.absolute().with_suffix(".mat"))
    matdata = scio.loadmat((modelpath.absolute().with_suffix(".mat")).__str__())
    hmm = []
    hmm.append(hmmstruct())
    hmm.append(hmmstruct())
    for i in range(2):
        hmm[i].N = matdata['hmm'][0][i][0][0][0][0].squeeze()
        hmm[i].M = matdata['hmm'][0][i][0][0][1][0].squeeze()
        hmm[i].init = np.float32(matdata['hmm'][0][i][0][0][2].squeeze())
        hmm[i].trans = np.float32(matdata['hmm'][0][i][0][0][3].squeeze())
        for j in range(hmm[i].N):
            hmm[i].mix[j].M = matdata['hmm'][0][i][0][0][4][0][j][0][0].squeeze()
            hmm[i].mix[j].mean = np.float32(matdata['hmm'][0][i][0][0][4][0][j][1])
            hmm[i].mix[j].var = np.float32(matdata['hmm'][0][i][0][0][4][0][j][2])
            hmm[i].mix[j].weight = np.float32(matdata['hmm'][0][i][0][0][4][0][j][3].squeeze())
    return hmm


def select_r(match="NBA", model="增量", level="第1档", hmm=None, train=False, dataindex=[1, 0], data0=None):
    if train:
        curpath = os.path.abspath(os.path.join(os.getcwd()))
        modelpath = "\\pack\\" + match + "\\" + model + "\\" + level
        datapath = "\\0\\数据集{}\\{}".format(dataindex[0], dataindex[1])
        path = curpath + modelpath + datapath
    else:
        path = None
    try:
        if model == "减量":
            data = readdata(train, 1, path, data0)
        else:
            data = readdata(train, 2, path, data0)
    except:
        a = 2
    else:
        pout = np.zeros([2, 1])
        for i in range(2):
            pout[i] = viterbi(hmm[i], data)
        a, b = max(enumerate(pout), key=operator.itemgetter(1))
    return a + 1


def prediction():
    try:
        #         with open("test.json") as fd:
        #                 data = json.load(fd)
        data = rq.post(f"{BASE_URL}/db/s", params={"collection": "email"}, json={"status": 0}).json()["data"]
        if not data:
            time.sleep(1)
            return
        matrix = texttonumpy(data[0])
        print(matrix)
        hmm = load_hmmmode(match=matrix[0], model=matrix[1], level=matrix[2])
        result = select_r(match=matrix[0], model=matrix[1], level=matrix[2], hmm=hmm, train=False, dataindex=None,
                          data0=matrix[3])
        rq.put(f"{BASE_URL}/db", params={"collection": "email"}, json={'_id': matrix[4], "status": result}).json()
    except Exception as e:
        print(e)
        time.sleep(2)


if __name__ == "__main__":
    while True:
        time.sleep(0.1)
        prediction()
#    仿真            
#    match = "NBA"
#    model = "增量"
#    N = 8
#    for i in range(1,6):
#          level = "第{}档".format(i)
#          hmm = load_hmmmode(match = match,model = model, level = level)
#          a = []
#          b = []
#          for k in range(1,3):
#                for j in range(N):                      
#                      result = select_r(match = match,model = model, level = level,hmm=hmm,train=True,dataindex=[k,j])
#                      if result >0 :
#                            a.append(result)
#                            b.append(k)
#          num = len(a)
#          num1 = 0
#          for i,v in enumerate(a):
#                if v == b[i]:
#                      num1 = num1+1
#          print(match+model+level+"命中率:{}".format(num1/num))
#    model = "减量"
#    N = 8
#    for i in range(1,6):
#          level = "第{}档".format(i)
#          hmm = load_hmmmode(match = match,model = model, level = level)
#          a = []
#          b = []
#          for k in range(1,3):
#                for j in range(N):                      
#                      result = select_r(match = match,model = model, level = level,hmm=hmm,train=True,dataindex=[k,j])
#                      if result >0 :
#                            a.append(result)
#                            b.append(k)
#          num = len(a)
#          num1 = 0
#          for i,v in enumerate(a):
#                if v == b[i]:
#                      num1 = num1+1
#          print(match+model+level+"命中率:{}".format(num1/num))
