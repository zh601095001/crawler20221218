from os import getenv

import requests as rq

BASE_URL = getenv("BASE_URL") or "http://localhost:8000"


def updateLastModify(lastModifyTime, lastModifyDate):
    rq.put(f"{BASE_URL}/db?collection=time", json={
        "_id": "lastRunTime",
        "lastModifyTime": lastModifyTime.__str__(),
        "lastModifyDate": lastModifyDate.__str__()
    })


def get_match_by_id(_id):
    return rq.get(f"{BASE_URL}/db", params={
        "_id": _id
    }).json()["data"]


def set_match_current(data: dict):
    return rq.put(f"{BASE_URL}/db", json=data)
