import hashlib
from datetime import datetime
from os import getenv
import time
from selenium import webdriver
from log import getLogger
from utils import loadJs, parseJSON, getProxy, updateStatus

SELENIUM = getenv("SELENIUM") or "http://127.0.0.1:4444"

logger = getLogger()


def convertMd5(s):
    return hashlib.md5(s.encode(encoding='utf-8')).hexdigest()


def getOptions():
    # proxys = getProxy()
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-gpu')
    options.add_argument("--disable-application-cache")
    options.add_argument('blink-settings=imagesEnabled=false')
    options.add_argument('--headless')
    # options.add_argument(f'--proxy-server=http://{proxys["proxys"]["http"]}')
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36")
    return [
        options,
        # proxys["_id"]
    ]


def getCurrent():
    """
    获取比赛当前信息
    """
    [
        options,
        # _id
    ] = getOptions()
    driver = webdriver.Remote(options=options, command_executor=SELENIUM)
    try:
        driver.get(f"http://live.nowscore.com/basketball.htm?date={datetime.now().date()}")
        datas = parseJSON(driver.execute_script(loadJs("./parser.js")))
        return datas
    except Exception as e:
        logger.error(f"抓取主页失败:{e}")
        # updateStatus(_id)
    finally:
        driver.quit()


def test1():
    st = time.time()
    count = 100
    for i in range(count):
        try:
            getCurrent()
        except Exception as e:
            count -= 1
    et = time.time()
    print(count)
    print((et - st) / count)


if __name__ == '__main__':
    pass
