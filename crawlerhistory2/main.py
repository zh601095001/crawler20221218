import time
from datetime import datetime, timedelta
from os import getenv

import yaml
from selenium import webdriver
from logging import config as loggingConfig, getLogger
from utils import loadJs, parseJSON, getDateTimeStampFromDatetime, getProxy, parser
from random import shuffle
from api import updateProxyStatus, search_match_without_records, update_match_records, add_new_matchs, getSettings

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


def getCurrent(date=datetime.now().date()):
    """
    获取比赛当前信息
    """
    options = getOptions()
    driver = webdriver.Remote(options=options, command_executor=SELENIUM)
    try:

        driver.get(f"http://live.nowscore.com/basketball.htm?date={date}")
        datas = parseJSON(driver.execute_script(loadJs("./parser.js", date.strftime("%m月%d日"))))
        return datas
    except Exception as e:
        logger.error(f"获取{date}的比赛失败：{e}")
    finally:
        driver.quit()


def getRecords():
    # proxy = getProxy()
    # try:
    matches = search_match_without_records()
    if len(matches) == 0:
        logger.info("数据抓取完毕")
        return
    shuffle(matches)
    data = matches[0]
    ID = data["ID"]
    _id = data["_id"]
    logger.info(f"_id:{_id},ID:{ID}")
    records = parser(ID)
    if records:
        logger.info(update_match_records(_id, records))
        logger.info(f"success:{ID}")
    # except Exception as e:
    #     print(e)
    #     logger.error(f"获取比赛记录失败:{e}")


def getLogs(previousDay=3):
    """
    获取记录
    :param start: 从第几天开始
    :param count: 往前统计多少天
    :return:
    """
    st = datetime.now()
    now = datetime.now()
    startDelta = timedelta(days=previousDay)
    dt = now - startDelta
    timeStamp = getDateTimeStampFromDatetime(dt)
    matches = getCurrent(dt.date())
    matches_valid = []
    for data in matches:
        ID = data["ID"]
        if not "letGoal" in data.keys():
            continue
        data["timeStamp"] = timeStamp
        data["_id"] = f"{timeStamp}-{ID}"
        matches_valid.append(data)
    logger.info(f"{dt.date()}下载的比赛：{matches_valid}")
    add_new_matchs(matches_valid)


if __name__ == '__main__':
    with open("logging_config.yml", "r", encoding="utf8") as f:
        logging_config = yaml.safe_load(f)
    loggingConfig.dictConfig(logging_config)
    logger = getLogger()
    while True:
        try:
            getLogs(3)  # 获取前前天的历史比赛数据
            getRecords()
            time.sleep(60 * 10)  # 10分钟间隔刷新
        except Exception as e:
            time.sleep(60 * 10)
            logger.error(e)
