import json
import time
from datetime import datetime

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


if __name__ == '__main__':
    js = loadJs("./parser.js")
    print(js)
