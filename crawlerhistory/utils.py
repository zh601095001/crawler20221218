import json
import re
import time
from datetime import datetime

import requests as rq
from os import getenv
import numpy as np

from bs4 import BeautifulSoup

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


def getDateTimeStampFromDatetime(dt: datetime):
    """
    获取当前日期的时间撮，不包括时分秒
    """
    return int(time.mktime(dt.date().timetuple()))


def getProxys(status=True):
    return rq.post(f"{BASE_URL}/db/s",
                   params={
                       "collection": "proxy"
                   },
                   json={
                       "isAlive": status
                   }).json()


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
    if datas:
        data = np.random.choice(datas)
        data["lastModify"] = int(time.time())
        rq.put(f"{BASE_URL}/db/s",
               params={
                   "collection": "proxy",
               },
               json=data)
        url = data["http"]
        username = "759126132"
        password = "sq6g9ci2"
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


def parser(_id, proxies):
    res = rq.get(f"http://live.nowscore.com/nba/odds/2in1Odds.aspx?cid=3&id={_id}", timeout=15, proxies=proxies)
    if res.status_code > 400:
        raise Exception(res.text)
    soup = BeautifulSoup(res.text, 'html.parser')
    tables = soup.find_all("table", class_="gts")
    if not tables:
        return
    changeRecord = tables[0]
    title = changeRecord.find("td", class_="ostitle").text
    headers = list(map(lambda td: td.text, changeRecord.find("tr", class_="gta").find_all("td")))

    def getRecords(record):
        return list(map(lambda td: td.text, record.find_all("td")))

    records = list(map(getRecords, changeRecord.find_all("tr", re.compile("gt[12]"))))
    return {
        "title": title,
        "headers": headers,
        "records": records
    }


if __name__ == '__main__':
    js = loadJs("./parser.js")
    print(js)
