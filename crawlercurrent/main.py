import yaml

from extract import getCurrent
from utils import updateLastModifyTime
from os import getenv
import requests as rq
from logging import config as loggingConfig, getLogger

BASE_URL = getenv("BASE_URL") or "http://localhost:8000"

if __name__ == '__main__':
    with open("logging_config.yml", "r", encoding="utf8") as f:
        logging_config = yaml.safe_load(f)
    loggingConfig.dictConfig(logging_config)
    logger = getLogger()
    while True:
        logger.info("执行中...")
        try:
            currentGames = getCurrent()
            logger.info(f"当前比赛：{currentGames}")
            if currentGames:
                updateLastModifyTime()
            for currentGame in currentGames:
                currentGame["_id"] = currentGame["ID"]
                res = rq.get(f"{BASE_URL}/db", params={
                    "_id": currentGame["ID"]
                })
                if not res.json()["data"]:
                    logger.info(f"比赛初始信息未找到,跳过...ID:{currentGame['ID']}")
                else:
                    logger.info(f"更新比赛：{currentGame['ID']}")
                    rq.put(f"{BASE_URL}/db", json=currentGame)
        except Exception as e:
            logger.error(f"全局错误:{e}")
