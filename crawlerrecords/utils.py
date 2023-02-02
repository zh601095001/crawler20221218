import json
import re
import time
from datetime import datetime
from random import shuffle
from bs4 import BeautifulSoup
from api import getLastRuntime, setLastRuntime, updateLastModify, getAliveProxy, getSettings, updateProxy, deAliveProxy
import requests as rq


def checkStartTime():
    startTime = int(time.time())
    if not getLastRuntime():
        setLastRuntime(startTime, datetime.now())


def updateLastModifyTime():
    lastModifyTime = int(time.time())
    updateLastModify(lastModifyTime, datetime.now())


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
    proxys = getAliveProxy()
    settings = getSettings()
    if not proxys:
        raise Exception("无法获取到代理ip")
    if not settings:
        raise Exception("请检查是否正确配置设置")
    username = settings["proxyUsername"]
    password = settings["proxyPassword"]
    if proxys:
        shuffle(proxys)
        proxy = proxys[0]
        proxy["lastModify"] = int(time.time())
        updateProxy(proxy)
        url = proxy["http"]
        proxy["proxys"] = {
            "http": "http://%(user)s:%(pwd)s@%(proxy)s/" % {"user": username, "pwd": password, "proxy": url},
            "https": "http://%(user)s:%(pwd)s@%(proxy)s/" % {"user": username, "pwd": password, "proxy": url}
        }
        return proxy
    else:
        return None


def updateStatus(_id):
    return deAliveProxy(_id)


def parser(_id, proxies):
    res = rq.get(f"http://live.nowscore.com/nba/odds/2in1Odds.aspx?cid=3&id={_id}", timeout=15, proxies=proxies)
    if res.status_code > 300:
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


def filterRecords(records):
    records.reverse()
    filtered = []
    filtered_ji = []
    for time, score, zhu, pan, ke, change, state in records:
        if time and score and pan and "封" not in pan and "加时" not in time and "中场" not in time:
            filtered.append([time, score, pan])
    for time, score, zhu, pan, ke, change, state in records:
        if "即" in state:
            filtered_ji.append(pan)
    return filtered, filtered_ji


def formatter(records, sep_time=12, isEffect=1):
    _records, records_ji = filterRecords(records)
    # 实时让分 真实分差 时间 有效性
    parts = [[_records[0]]]
    for i in _records[1:]:
        last_elm = parts[-1][-1]  # 选择该节中最后一个元素
        if last_elm[0].strip().split()[0] == i[0].strip().split()[0]:
            parts[-1].append(i)
        else:
            parts.append([i])
    result_arr = []
    for i, part in enumerate(parts):
        start = i * 12 * 60
        for t, score, letScore in part:
            if len(t.strip().split()) < 2:
                continue
            t = list(map(lambda x: int(x), t.strip().split()[1].split(":")))
            seconds = t[0] * 60 + t[1]
            currentTime = start + (sep_time * 60 - seconds)
            letScore = float(letScore)
            result_arr.append([letScore, eval(score), currentTime, isEffect])
    length = len(result_arr)
    length_ji = len(records_ji)
    if length_ji > length:
        result_arr.extend([[None, None, None] for i in range(length_ji - length)])
    else:
        records_ji.extend([0 for i in range(length - length_ji)])
    result_arr2 = []
    for res, _ in zip(result_arr, records_ji):
        temp = [_]
        temp.extend(res)
        temp = map(lambda x: str(x), temp)
        result_arr2.append(temp)
    csv = [",".join(["即", "滚盘", "真实分差", "时间", "结果"])]
    result_arr2 = list(map(lambda x: ",".join(x), result_arr2))
    csv.extend(result_arr2)
    return "\n".join(csv)


if __name__ == '__main__':
    js = loadJs("./parser.js")
    print(js)
