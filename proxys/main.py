import time
from os import getenv
from hashlib import md5
import requests as rq
import random
import kdl

BASE_URL = getenv("BASE_URL") or "http://localhost:8000"


def getIps(num):
    settings = rq.post(f"{BASE_URL}/db/s",
                       params={
                           "collection": "settings"
                       },
                       json={
                           "_id": "basicSettings"
                       }).json()["data"][0]
    secretId = settings["secretId"]
    secretKey = settings["secretKey"]
    auth = kdl.Auth(secretId, secretKey)
    client = kdl.Client(auth)
    ips = client.get_dps(num, format='json')
    valids = client.check_dps_valid(ips)
    valids = list(filter(lambda i: i, [k if v else None for k, v in valids.items()]))
    return valids


def updateProxy(num=1):
    urls = getIps(num)
    urls = list(map(lambda url: {"_id": md5(f"http://{url}".encode("utf-8")).hexdigest(), "http": f"{url}", "created": int(time.time()), "isAlive": True,
                                 "lastModify": int(time.time())}, urls))
    return rq.post(f"{BASE_URL}/db", params={
        "collection": "proxy"
    }, json=urls).json()


def get(status=True):
    return rq.post(f"{BASE_URL}/db/s",
                   params={
                       "collection": "proxy"
                   },
                   json={
                       "isAlive": status
                   }).json()


def updateStatus(_id, status=False):
    return rq.put(f"{BASE_URL}/db", params={
        "collection": "proxy"
    }, json={
        "_id": _id,
        "isAlive": status
    }).json()


def checkAlive(aliveCount=50, newCount=50):
    """
    当不足aliveCount时，添加newCount个代理
    """
    if len(get()["data"]) < aliveCount:
        return updateProxy(newCount)


def log(obj: [list, dict]):
    if obj:
        return rq.post(f"{BASE_URL}/db", params={
            "collection": "logs"
        }, json={
            "_id": int(time.time()),
            "data": obj
        }).json()
    else:
        return False


if __name__ == '__main__':
    while True:
        try:
            settings = rq.post(f"{BASE_URL}/db/s",
                               params={
                                   "collection": "settings"
                               },
                               json={
                                   "_id": "basicSettings"
                               }).json()["data"][0]
            count = settings["proxyNumber"]
            log(checkAlive(aliveCount=count, newCount=count))
        except Exception as e:
            time.sleep(1)
            print(e)
