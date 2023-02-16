import time
from os import getenv
import uvicorn
from fastapi import FastAPI, HTTPException
from selenium import webdriver

from log import getLogger
from utils import getProxy, updateStatus, parser, formatter

SELENIUM = getenv("SELENIUM") or "http://127.0.0.1:4444"

logger = getLogger()


def getOptions():
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-gpu')
    options.add_argument("--disable-application-cache")
    options.add_argument('blink-settings=imagesEnabled=false')
    options.add_argument('--headless')
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36")

    return options


def getRecords(_id):
    proxy = None
    # try:
    #     proxy = getProxy()
    # except Exception as e:
    #     logger.error(e)
    # if not proxy:
    #     logger.info(f"未能从代理列表获取代理，{proxy}")
    try:
        logger.info(f"_id:{_id}")
        records = parser(_id,)
                         # proxy["proxys"])
        if records:
            return records
        else:
            return None
    except Exception as e:
        logger.error(f"获取比赛记录失败:{e}")
        # if proxy:
        #     updateStatus(proxy["_id"])
        return None


app = FastAPI()


@app.get("/records")  # 获取所有联赛名
async def get_records_by_id(_id: str, sep_time: int = 12, isEffect: int = 1):
    max_retry = 20
    count = 0
    while True:
        count += 1
        if count > max_retry:
            # 尝试失败
            raise HTTPException(status_code=404, detail="获取失败...")
        records = getRecords(_id)
        if records:
            return formatter(records["records"], sep_time=sep_time, isEffect=isEffect)
        else:
            time.sleep(30)


if __name__ == '__main__':
    config = uvicorn.Config("main:app", port=6000, log_level="info", host="0.0.0.0", workers=20)
    server = uvicorn.Server(config)
    server.run()
