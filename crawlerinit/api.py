from os import getenv

import requests as rq

BASE_URL = getenv("BASE_URL") or "http://localhost:8000"


def get_match_by_id(_id):
    return rq.get(f"{BASE_URL}/db", params={
        "_id": _id
    }).json()["data"]


def add_new_match(match: dict):
    return rq.post(f"{BASE_URL}/db", json=match)


def update_match(match: dict):
    return rq.put(f"{BASE_URL}/db", json=match)
