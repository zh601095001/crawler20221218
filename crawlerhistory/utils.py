import json
import re
import time
from datetime import datetime
from random import shuffle
import requests as rq
from bs4 import BeautifulSoup
from api import getAliveProxys, getSettings, updateProxys


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


def getProxy():
    proxys = getAliveProxys()
    settings = getSettings()
    username = settings["proxyUsername"]
    password = settings["proxyPassword"]
    if proxys:
        shuffle(proxys)
        proxy = proxys[0]
        proxy["lastModify"] = int(time.time())
        updateProxys(proxy)
        proxy["proxys"] = {
            "http": "http://%(user)s:%(pwd)s@%(proxy)s/" % {"user": username, "pwd": password, "proxy": proxy["http"]},
            "https": "http://%(user)s:%(pwd)s@%(proxy)s/" % {"user": username, "pwd": password, "proxy": proxy["http"]}
        }
        return proxy
    else:
        return None


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
