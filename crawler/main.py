from extract import getInit, getCurrent
from utils import updateLastModifyTime, checkStartTime
from os import getenv
import requests as rq

BASE_URL = getenv("BASE_URL") or "http://localhost:8000"

while True:
    try:
        checkStartTime()
        currentGames = getCurrent(env="")
        print(currentGames)
        if currentGames:
            updateLastModifyTime()
        isNew = True
        for currentGame in currentGames:
            _id = currentGame["_id"]
            print(_id)
            res = rq.get(f"{BASE_URL}/db", params={
                "_id": _id
            })
            print("data:", res.json()["data"])
            if not res.json()["data"]:
                isNew = False
                break
            else:
                res2 = rq.put(f"{BASE_URL}/db", json=currentGame)
        print(isNew)
        if not isNew:
            initGames = getInit(env="")
            print("init:", initGames)
            for initGame in initGames:
                _id = initGame["_id"]
                res = rq.get(f"{BASE_URL}/db", params={
                    "_id": _id
                })
                if not res.json()["data"]:
                    initGame["isSendEmail"] = False
                    res1 = rq.post(f"{BASE_URL}/db", json=initGame)


    except Exception as e:
        with open("log.txt", "a+") as fd:
            fd.write(str(e))
            print(e)
