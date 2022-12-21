import time
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
            "lastModifyTime": startTime
        })


def updateLastModifyTime():
    lastModifyTime = int(time.time())
    res2 = rq.put(f"{BASE_URL}/db?collection=time", json={
        "_id": "lastRunTime",
        "lastModifyTime": lastModifyTime,
    })
