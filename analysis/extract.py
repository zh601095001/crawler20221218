from datetime import datetime, timedelta
from os import getenv
from selenium import webdriver
import re
from bs4 import BeautifulSoup
import requests as rq
from utils import loadJs, parseJSON, getDateTimeStampFromDatetime, BASE_URL

SELENIUM = getenv("SELENIUM") or "http://127.0.0.1:4444"


def parser(_id):
    soup = BeautifulSoup(rq.get(f"http://live.nowscore.com/nba/odds/2in1Odds.aspx?cid=3&id={_id}").text, 'html.parser')
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


def getOptions():
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-gpu')
    options.add_argument("--disable-application-cache")
    options.add_argument('blink-settings=imagesEnabled=false')
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36")
    return options


def getCurrent(date=datetime.now().date(), env="dev"):
    """
    获取比赛当前信息
    """
    options = getOptions()
    if env == "dev":
        driver = webdriver.Chrome(options=options)
    else:
        options.add_argument('--headless')
        driver = webdriver.Remote(options=options, command_executor=SELENIUM)

    driver.get(f"http://live.nowscore.com/basketball.htm?date={date}")
    datas = parseJSON(driver.execute_script(loadJs("./parser.js")))
    driver.quit()

    return datas


def getLogs(start=1, count=365):
    """
    获取记录
    :param start: 从第几天开始
    :param count: 往前统计多少天
    :return:
    """
    logs = []
    for i in range(start, count + 1):
        now = datetime.now()
        startDelta = timedelta(days=i)
        dt = now - startDelta
        timeStamp = getDateTimeStampFromDatetime(dt)
        print(timeStamp)
        datas = getCurrent(dt.date(), env="")
        for data in datas:
            ID = data["ID"]
            data["_id"] = f"{timeStamp}-{ID}"
            data["records"] = parser(ID)
            logs.append(data)
    return logs


def save(datas: list):
    return rq.post(f"{BASE_URL}/db?collection=matchLogs", json=datas).json()


if __name__ == '__main__':
    getLogs(1, 1)
