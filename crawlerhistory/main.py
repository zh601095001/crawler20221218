import time
from datetime import datetime, timedelta
from os import getenv
from selenium import webdriver
import requests as rq
from utils import loadJs, parseJSON, getDateTimeStampFromDatetime, BASE_URL, getProxy, updateStatus, parser
from random import shuffle
from log import getLogger

SELENIUM = getenv("SELENIUM") or "http://127.0.0.1:4444"

logger = getLogger()


def getOptions():
    # proxys = getProxy()
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-gpu')
    options.add_argument("--disable-application-cache")
    options.add_argument('blink-settings=imagesEnabled=false')
    # options.add_argument(f'--proxy-server=http://{proxys["proxys"]["http"]}')
    options.add_argument('--headless')
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36")

    return [
        options,
        # proxys["_id"]
    ]


def getCurrent(date=datetime.now().date()):
    """
    获取比赛当前信息
    """
    [
        options,
        # _id
    ] = getOptions()
    driver = webdriver.Remote(options=options, command_executor=SELENIUM)
    try:

        driver.get(f"http://live.nowscore.com/basketball.htm?date={date}")
        datas = parseJSON(driver.execute_script(loadJs("./parser.js", date.strftime("%m月%d日"))))
        return datas
    except Exception as e:
        logger.error(f"获取{date}的比赛失败：{e}")
        # updateStatus(_id)
    finally:
        driver.quit()


def getRecords(useProxy=True):
    proxy = getProxy()
    try:
        datas = rq.post(f"{BASE_URL}/db/s?collection=matches", json={
            "records": None,
            "limit": 100
        }).json()["data"]
        if len(datas) == 0:
            print("数据抓取完毕")
            return
        shuffle(datas)
        data = datas[0]
        ID = data["ID"]
        _id = data["_id"]
        logger.info(f"_id:{_id},ID:{ID}")
        records = parser(ID, proxy["proxys"] if useProxy else None)
        if records:
            res = rq.put(f"{BASE_URL}/db?collection=matches", json={
                "records": records,
                "_id": _id
            }).json()
            logger.info(res)
            logger.info(f"success:{ID}")
    except Exception as e:
        logger.error(f"获取比赛记录失败:{e}")
        updateStatus(proxy["_id"])


def getLogs(start=1, count=365):
    """
    获取记录
    :param start: 从第几天开始
    :param count: 往前统计多少天
    :return:
    """
    logs = []
    st = datetime.now()
    for i in range(start, count + 1):
        now = datetime.now()
        startDelta = timedelta(days=i)
        dt = now - startDelta
        timeStamp = getDateTimeStampFromDatetime(dt)
        datas = getCurrent(dt.date())
        logger.info(f"{dt.date()}需要下载的比赛：{datas}")
        for data in datas:
            ID = data["ID"]
            data["timeStamp"] = timeStamp
            data["_id"] = f"{timeStamp}-{ID}"
        logs.append(rq.post(f"{BASE_URL}/db?collection=matches", json=datas).json())
        logger.info(f"历史条目进度：{i / count * 100:.2f}% 用时：{datetime.now() - st}")
    return logs


if __name__ == '__main__':
    settings = rq.post(f"{BASE_URL}/db/s",
                       params={
                           "collection": "settings"
                       },
                       json={
                           "_id": "basicSettings"
                       }).json()["data"][0]
    day = settings["historyCrawlerDay"]
    logs = getLogs(2, day)
    while True:
        try:
            time.sleep(60)
            getRecords(True)
        except Exception as e:
            print(e)
