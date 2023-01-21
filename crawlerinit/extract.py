import hashlib
import re
from datetime import datetime
from os import getenv
import requests as rq
from bs4 import BeautifulSoup
from selenium import webdriver

from utils import loadJs, parseJSON

SELENIUM = getenv("SELENIUM") or "http://127.0.0.1:4444"


def convertMd5(s):
    return hashlib.md5(s.encode(encoding='utf-8')).hexdigest()


def getOptions():
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-gpu')
    options.add_argument("--disable-application-cache")
    options.add_argument('blink-settings=imagesEnabled=false')
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36")
    return options


def getInit(env="dev"):
    """
    获取比赛初始信息
    """
    options = getOptions()
    if env == "dev":
        driver = webdriver.Chrome(options=options)
    else:
        options.add_argument('--headless')
        driver = webdriver.Remote(options=options, command_executor=SELENIUM)
    driver.get(f"http://live.nowscore.com/basketball.htm?date={datetime.now().date()}")
    lives = parseJSON(driver.execute_script(loadJs("./parser.js")))
    driver.quit()
    for live in lives:
        soup = BeautifulSoup(rq.get(f"http://live.nowscore.com/nba/odds/2in1Odds.aspx?cid=3&id={live['ID']}").text,
                             'html.parser')
        tables = soup.find_all("table", class_="gts")
        if not tables:
            continue
        changeRecord = tables[0]

        def getRecords(record):
            return list(map(lambda td: td.text, record.find_all("td")))

        records = list(map(getRecords, changeRecord.find_all("tr", re.compile("gt[12]"))))
        records.reverse()
        try:
            firstCount = records[0][3]
            countRecords = []
            for record in records:
                if not record[0]:
                    countRecords.append(record)
                else:
                    break
            lastCount = countRecords[-1][3]
            firstCount = float(firstCount)
            lastCount = float(lastCount)
        except Exception as e:
            print(e)
            firstCount = None
            lastCount = None
        live["firstCount"] = firstCount
        live["lastCount"] = lastCount
    return lives


def testInit():
    getInit(env="")


if __name__ == '__main__':
    testInit()
