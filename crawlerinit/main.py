from logging import config as loggingConfig, getLogger
import time

import yaml

from extract import getInit
from utils import checkStartTime
from os import getenv
import requests as rq

BASE_URL = getenv("BASE_URL") or "http://localhost:8000"

if __name__ == '__main__':
    with open("logging_config.yml", "r", encoding="utf8") as f:
        logging_config = yaml.safe_load(f)
    loggingConfig.dictConfig(logging_config)
    logger = getLogger()
    while True:
        time.sleep(5)
        logger.info("执行中...")
        try:
            checkStartTime()
            initGames = getInit()
            logger.info(f"初始比赛：{initGames}")
            for initGame in initGames:
                initGame["_id"] = initGame["ID"]
                res = rq.get(f"{BASE_URL}/db", params={
                    "_id": initGame["ID"]
                })
                if not res.json()["data"]:
                    initGame["createTime"] = int(time.time())
                    initGame["isSendEmail"] = False
                    rq.post(f"{BASE_URL}/db", json=initGame)
                else:
                    rq.put(f"{BASE_URL}/db", json=initGame)
        except Exception as e:
            logger.error(f"初始让分全局错误:{e}")
