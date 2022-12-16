import re
import requests as rq
from extract import Extarct
import time

extract = Extarct()

startTime = int(time.time())
res = rq.get(f"http://localhost:8000/db?collection=time", params={
    "_id": "lastRunTime"
})
if not res.json()["data"]:
    res1 = rq.post(f"http://localhost:8000/db?collection=time", json={
        "_id": "lastRunTime",
        "createTime": startTime,
    })
    # print(res1.text)
else:
    res2 = rq.put(f"http://localhost:8000/db?collection=time", json={
        "_id": "lastRunTime",
        "createTime": startTime,
    })
while True:
    time.sleep(0.1)
    tables = extract.run()
    for table in tables:
        startTime = table[0][0]
        title1 = re.match("^<a.*?>(.*?)</a>$", table[1][0]).group(1)
        title2 = re.match("^<a.*?>(.*?)</a>$", table[2][0]).group(1)
        titles = "|".join([title1, title2])
        print(titles)
        score = 0
        score1Match = re.match("^<span.*?>(.*?)</span><span.*?>.*?</span>$", table[1][10])
        if score1Match:
            score1 = score1Match.group(1)
            score += float(score1)
        score2Match = re.match("^<span.*?>(.*?)</span><span.*?>.*?</span>$", table[2][10])
        if score2Match:
            score2 = score2Match.group(1)
            score -= float(score2)
        print(score)

        _id = f"{startTime} {titles}"
        now = int(time.time())
        res = rq.get(f"http://localhost:8000/db", params={
            "_id": _id
        })
        if not res.json()["data"]:
            res1 = rq.post(f"http://localhost:8000/db", json={
                "_id": _id,
                "createTime": now,
                "isSendEmail": False,
                now: {"raw": table, "score": score},
            })
            # print(res1.text)
        else:
            res2 = rq.put(f"http://localhost:8000/db", json={
                "_id": _id,
                now: {"raw": table, "score": score},
            })
            # print(res2.text)
        print("-----------")
