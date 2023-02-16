import re
import time
from datetime import datetime
from os import getenv
import requests as rq
from bs4 import BeautifulSoup
from selenium import webdriver
import logging
from utils import loadJs, parseJSON, getProxy, updateStatus
from api import get_match_by_id

SELENIUM = getenv("SELENIUM") or "http://127.0.0.1:4444"


def getOptions():
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-gpu')
    options.add_argument("--disable-application-cache")
    options.add_argument('blink-settings=imagesEnabled=false')
    options.add_argument('--headless')
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36")
    return options


def getLives():
    """
    获取比赛初始信息
    """
    logger = logging.getLogger()
    options = getOptions()
    driver = webdriver.Remote(options=options, command_executor=SELENIUM)
    driver.set_page_load_timeout(20)
    driver.set_script_timeout(20)
    try:
        driver.get(f"http://live.nowscore.com/basketball.htm?date={datetime.now().date()}")
        return parseJSON(driver.execute_script(loadJs("./parser.js")))
    except Exception as e:
        logger.error(e)
    finally:
        driver.quit()


def getinitScore(_id):
    logger = logging.getLogger()
    # proxys = getProxy()
    # if not proxys:
    #     logger.warning(f"代理列表为空：{proxys}")
    #     return
    response = None
    try:
        response = rq.get(f"http://live.nowscore.com/nba/odds/2in1Odds.aspx?cid=3&id={_id}",
                          # proxies=proxys["proxys"]
                          )
    except Exception as e:
        logger.warning(f"can not response from server,{e}")
        # logger.warning(f"代理失效:{e}")
        # updateStatus(proxys["_id"])
        # return
    if response.status_code > 300:
        # logger.error(f"未能从代理服务器获取数据，响应失败,code：{response.status_code}，{response.text}")
        # updateStatus(proxys["_id"])
        logger.warning(f"can not response from server,{e}")
        return
    soup = BeautifulSoup(response.text, 'html.parser')
    tables = soup.find_all("table", class_="gts")
    if not tables:
        return

    def getRecords(record):
        return list(map(lambda td: td.text, record.find_all("td")))

    records = list(map(getRecords, tables[0].find_all("tr", re.compile("gt[12]"))))
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
        if firstCount and lastCount:
            return firstCount, lastCount
    except Exception as e:
        logger.info(f"未获取到初始让分:{e}")


def getInit():
    lives = getLives()
    logger = logging.getLogger()
    newLives = []  # 获取到初始让分的比赛
    for live in lives:
        time.sleep(5)
        try:
            # 查看数据库是否已存在该比赛 存在则跳过
            if get_match_by_id(live["ID"]):
                logger.info(f"比赛:{live['ID']}|【{live['hometeam'][0]} vs {live['guestteam'][0]}】,已经记录，跳过...")
                continue
            # 如果不存在初始让分 跳过
            if "letGoal" not in live.keys():
                logger.info(f"比赛:{live['ID']}|【{live['hometeam'][0]} vs {live['guestteam'][0]}】,无初始让分，跳过...")
                continue
            scores = getinitScore(live["ID"])
            if scores:
                live["firstCount"] = scores[0]
                live["lastCount"] = scores[1]
                logger.info(f"比赛:{live['ID']}|【{live['hometeam'][0]} vs {live['guestteam'][0]}】,初始让分：{scores[0]} {scores[1]}")
                newLives.append(live)
        except Exception as e:
            logger.error(e)
    return newLives
