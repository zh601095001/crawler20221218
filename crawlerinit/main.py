import time

from extract import getInit
from utils import checkStartTime
from os import getenv
import requests as rq
from log import getLogger

BASE_URL = getenv("BASE_URL") or "http://localhost:8000"
logger = getLogger()


def init_process():
    while True:
        time.sleep(5)
        try:
            checkStartTime()
            initGames = getInit()
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


if __name__ == '__main__':
    print("starting...")
    init_process()
    print("successfully!")
