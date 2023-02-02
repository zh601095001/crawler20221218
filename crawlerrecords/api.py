import time
from os import getenv
import requests as rq

BASE_URL = getenv("BASE_URL") or "http://localhost:8000"


def getLastRuntime():
    res = rq.get(f"{BASE_URL}/db?collection=time", params={
        "_id": "lastRunTime"
    }).json()
    return res["data"]


def setLastRuntime(createTime, createDate):
    rq.post(f"{BASE_URL}/db?collection=time", json={
        "_id": "lastRunTime",
        "createTime": createTime.__str__(),
        "createDate": createDate.__str__()
    })


def updateLastModify(lastModifyTime, lastModifyDate):
    rq.put(f"{BASE_URL}/db?collection=time", json={
        "_id": "lastRunTime",
        "lastModifyTime": lastModifyTime.__str__(),
        "lastModifyDate": lastModifyDate.__str__()
    })


def getAliveProxy():
    data = rq.post(f"{BASE_URL}/db/s",
                   params={
                       "collection": "proxy",
                   },
                   json={
                       "limit": 4000,
                       "isAlive": True,
                       "lastModify": {"$lt": int(time.time()) - 1}
                   }).json()["data"]
    return data if data else None


def getSettings():
    data = rq.post(f"{BASE_URL}/db/s",
                   params={
                       "collection": "settings"
                   },
                   json={
                       "_id": "basicSettings"
                   }).json()["data"]
    if data:
        return data[0]
    else:
        return None


def updateProxy(data: dict):
    rq.put(f"{BASE_URL}/db",
           params={
               "collection": "proxy",
           },
           json=data)


def deAliveProxy(_id):
    return rq.put(f"{BASE_URL}/db", params={
        "collection": "proxy"
    }, json={
        "_id": _id,
        "isAlive": False,
        "lastModify": int(time.time())
    }).json()
