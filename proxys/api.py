from os import getenv

import requests as rq

BASE_URL = getenv("BASE_URL") or "http://localhost:8000"


def getSettings():
    settings = rq.post(f"{BASE_URL}/db/s",
                       params={
                           "collection": "settings"
                       },
                       json={
                           "_id": "basicSettings"
                       }).json()["data"]
    if settings:
        return settings[0]


def updateProxys(data: list):
    return rq.put(f"{BASE_URL}/db", params={
        "collection": "proxy"
    }, json=data).json()


def getAliveProxys():
    return rq.post(f"{BASE_URL}/db/s",
                   params={
                       "collection": "proxy"
                   },
                   json={
                       "isAlive": True
                   }).json()["data"]
