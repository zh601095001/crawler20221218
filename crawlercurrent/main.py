from extract import getCurrent
from utils import updateLastModifyTime
from os import getenv
import requests as rq
from log import getLogger

BASE_URL = getenv("BASE_URL") or "http://localhost:8000"

logger = getLogger()


def curr_process():
    while True:
        try:
            currentGames = getCurrent()
            if currentGames:
                updateLastModifyTime()
            for currentGame in currentGames:
                currentGame["_id"] = currentGame["ID"]
                res = rq.get(f"{BASE_URL}/db", params={
                    "_id": currentGame["ID"]
                })
                if not res.json()["data"]:
                    pass
                else:
                    rq.put(f"{BASE_URL}/db", json=currentGame)
        except Exception as e:
            logger.error(f"全局错误:{e}")


if __name__ == '__main__':
    print("starting...")
    curr_process()
    print("successfully!")
