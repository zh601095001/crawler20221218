import json
from os import getenv
import requests as rq
from datetime import datetime, timedelta

from pandas import DataFrame

from utils import getDateTimeStampFromDatetime

ANALYSIS_URL = getenv("ANALYSIS_URL") or "http://localhost:5000"
BASE_URL = getenv("BASE_URL") or "http://localhost:8000"


def getRecent():
    """获取前前天的比赛名"""
    datenow = datetime.now()
    threeDaysAgo = getDateTimeStampFromDatetime(datenow - timedelta(days=3))
    fourDaysAgo = getDateTimeStampFromDatetime(datenow - timedelta(days=4))
    res = rq.post(f"{BASE_URL}/db/s", params={"collection": "matches"}, json={
        "timeStamp": {
            "$gt": fourDaysAgo,
            "$lt": threeDaysAgo
        }
    }).json()
    s = set()
    for i in res["data"]:
        s.add(i["sclassName"][0])
    return list(s)


def getAllMatchNames(dateRange):
    data = rq.post(f"{BASE_URL}/db/s?collection=matches", json={
        "timeStamp": {"$gte": dateRange[0], "$lte": dateRange[1]},
        "records.records": {"$not": {"$size": 0}},
        "$projection": {
            "sclassName": 1,
            "ID": 1
        },
        "limit": 999999999
    }).json()
    df = DataFrame(data["data"])
    df["sclassName"] = df["sclassName"].map(lambda item: item[0])
    return json.loads(df.groupby("sclassName")["ID"].count().to_json())


if __name__ == '__main__':
    print(getRecent())
