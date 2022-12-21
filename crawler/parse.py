import re
import time

import requests as rq
from os import getenv

BASE_URL = getenv("BASE_URL") or "http://localhost:8000"


def parseTables(tables):
    for table in tables:
        startTime = table[0][0]
        title1 = re.match("^<a.*?>(.*?)</a>$", table[1][0]).group(1)
        title2 = re.match("^<a.*?>(.*?)</a>$", table[2][0]).group(1)
        titles = "|".join([title1, title2])
        score = 0
        score1Match = re.match("^<span.*?>(.*?)</span><span.*?>.*?</span>$", table[1][10])
        if score1Match:
            score1 = score1Match.group(1)
            score += float(score1)
        score2Match = re.match("^<span.*?>(.*?)</span><span.*?>.*?</span>$", table[2][10])
        if score2Match:
            score2 = score2Match.group(1)
            score -= float(score2)
        print(f"{titles}:{score}")

        _id = f"{startTime} {titles}"
        now = int(time.time())
        res = rq.get(f"{BASE_URL}/db", params={
            "_id": _id
        })
        if not res.json()["data"]:
            res1 = rq.post(f"{BASE_URL}/db", json={
                "_id": _id,
                "createTime": now,
                "isSendEmail": False,
                "start": {"now": now, "score": score},
            })
            # print(res1.text)
        else:
            res2 = rq.put(f"{BASE_URL}/db", json={
                "_id": _id,
                "end": {"now": now, "score": score},
            })
            # print(res2.text)
    print("-----------")
