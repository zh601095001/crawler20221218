import hashlib
from datetime import datetime
from os import getenv
import time
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
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36")
    return options


def getCurrent(env="dev"):
    """
    获取比赛当前信息
    """
    options = getOptions()
    if env == "dev":
        driver = webdriver.Chrome(options=options)
    else:
        options.add_argument('--headless')
        driver = webdriver.Remote(options=options, command_executor=SELENIUM)

    driver.get(f"http://live.nowscore.com/basketball.htm?date={datetime.now().date()}")
    datas = parseJSON(driver.execute_script(loadJs("./parser.js")))
    driver.quit()

    return datas


def test1():
    st = time.time()
    count = 100
    for i in range(count):
        try:
            getCurrent(env="")
        except Exception as e:
            count -= 1
    et = time.time()
    print(count)
    print((et - st) / count)


if __name__ == '__main__':
    pass
