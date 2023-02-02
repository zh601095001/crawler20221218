from os import getenv
import time
import requests as rq

BASE_URL = getenv("BASE_URL") or "http://localhost:8000"


def getAliveProxys():
    return rq.post(f"{BASE_URL}/db/s",
                   params={
                       "collection": "proxy",
                   },
                   json={
                       "limit": 4000,
                       "isAlive": True,
                       "lastModify": {"$lt": int(time.time()) - 1}
                   }).json()["data"]


def updateProxys(proxy: dict):
    return rq.put(f"{BASE_URL}/db",
                  params={
                      "collection": "proxy",
                  },
                  json=proxy)


def updateProxyStatus(_id):
    return rq.put(f"{BASE_URL}/db", params={
        "collection": "proxy"
    }, json={
        "_id": _id,
        "isAlive": False,
        "lastModify": int(time.time())
    }).json()


def getSettings():
    settings = rq.post(f"{BASE_URL}/db/s",
                       params={
                           "collection": "settings"
                       },
                       json={
                           "_id": "basicSettings"
                       }).json()["data"]
    if not settings:
        raise Exception("请检查基础配置是否正确")
    return settings[0]


def search_match_without_records():
    return rq.post(f"{BASE_URL}/db/s?collection=matches", json={
        "records": None,
        "limit": 100
    }).json()["data"]


def update_match_records(_id, records):
    return rq.put(f"{BASE_URL}/db?collection=matches", json={
        "records": records,
        "_id": _id
    }).json()["data"]


def add_new_matchs(matchs):
    return rq.post(f"{BASE_URL}/db?collection=matches", json=matchs).json()
