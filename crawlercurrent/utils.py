import json
import time
from datetime import datetime
from random import shuffle
import requests as rq
from os import getenv

BASE_URL = getenv("BASE_URL") or "http://localhost:8000"


def checkStartTime():
    startTime = int(time.time())
    res = rq.get(f"{BASE_URL}/db?collection=time", params={
        "_id": "lastRunTime"
    })
    if not res.json()["data"]:
        rq.post(f"{BASE_URL}/db?collection=time", json={
            "_id": "lastRunTime",
            "createTime": startTime,
            "createDate": datetime.now().__str__()
        })


def updateLastModifyTime():
    lastModifyTime = int(time.time())
    rq.put(f"{BASE_URL}/db?collection=time", json={
        "_id": "lastRunTime",
        "lastModifyTime": lastModifyTime,
        "lastModifyDate": datetime.now().__str__()
    })


def justifyArgs(arg):
    if type(arg) in [int, float]:
        return f"{arg}"
    else:
        return f"'{arg}'"


def loadJs(path, *args):
    with open(path) as fd:
        lines = fd.readlines()[0:-1]
        postArgs = map(justifyArgs, args)
        script_args = f"({','.join(postArgs)})"
        lines.append(script_args)
        return "return" + "\n".join(lines)


def parseJSON(s: str):
    return json.loads(s)


def getProxy(status=True):
    datas = rq.post(f"{BASE_URL}/db/s",
                    params={
                        "collection": "proxy",
                    },
                    json={
                        "limit": 4000,
                        "isAlive": status,
                        "lastModify": {"$lt": int(time.time()) - 1}
                    }).json()["data"]
    settings = rq.post(f"{BASE_URL}/db/s",
                       params={
                           "collection": "settings"
                       },
                       json={
                           "_id": "basicSettings"
                       }).json()["data"][0]
    username = settings["proxyUsername"]
    password = settings["proxyPassword"]
    if datas:
        shuffle(datas)
        data = datas[0]
        data["lastModify"] = int(time.time())
        rq.put(f"{BASE_URL}/db",
               params={
                   "collection": "proxy",
               },
               json=data)
        url = data["http"]
        data["proxys"] = {
            "http": "http://%(user)s:%(pwd)s@%(proxy)s/" % {"user": username, "pwd": password, "proxy": url},
            "https": "http://%(user)s:%(pwd)s@%(proxy)s/" % {"user": username, "pwd": password, "proxy": url}
        }
        return data
    else:
        return None


def updateStatus(_id, status=False):
    return rq.put(f"{BASE_URL}/db", params={
        "collection": "proxy"
    }, json={
        "_id": _id,
        "isAlive": status,
        "lastModify": int(time.time())
    }).json()


if __name__ == '__main__':
    js = loadJs("./parser.js", 100, 10.5, "a")
    print(js)
