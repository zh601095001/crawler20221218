import os
import time
from pathlib import Path
from fastapi import FastAPI, WebSocket
from pydantic import BaseModel
from datetime import datetime
from analysis import analysis_matches_by_name
import uvicorn
import json
from starlette.responses import FileResponse

from api import getRecent, getAllMatchNames
from utils import convert, zipDir

app = FastAPI()


def getDateTimeStampFromDatetime(dt: datetime):
    """
    获取当前日期的时间撮，不包括时分秒
    """
    return int(time.mktime(dt.date().timetuple()))


class Range(BaseModel):
    min: int
    max: int


class Analysis(BaseModel):  # 构造
    matchName: list
    range: Range
    q: int


def convertDateRange(dateRange: str):
    return list(map(lambda x: getDateTimeStampFromDatetime(datetime.fromtimestamp(int(x[:-3]))), dateRange.split(",")))


@app.get("/matches")  # 获取所有联赛名
async def get_all_matches_name(dateRange: str):
    dateRange = convertDateRange(dateRange)
    return getAllMatchNames(dateRange)


@app.post("/matches")
async def analysis_matches(dateRange: str, obj: Analysis):
    dateRange = convertDateRange(dateRange)
    return analysis_matches_by_name(obj.matchName, dateRange, obj.q, (obj.range.min, obj.range.max))


@app.delete("/matches")
async def delete_matches_cache():
    path = Path(".")
    download = path / "download"
    result = path / "result"


@app.get("/download")
async def analysis_matches(dateRange: str, obj: str):
    obj = json.loads(obj)
    dateRange = convertDateRange(dateRange)
    packRoot = Path("zips")
    data = analysis_matches_by_name(obj["matchName"], dateRange, obj["q"], (obj["range"]["min"], obj["range"]["max"]))
    convert(data, packRoot)
    zipDir(packRoot, "pack.zip")
    os.system(f"rm zips -r")
    return FileResponse('pack.zip', filename='pack.zip')


@app.websocket("/recommendws")
async def getMatchHistory(websocket: WebSocket):
    await websocket.accept()
    data = json.loads(await websocket.receive_text())
    dateRange = convertDateRange(data["dateRange"])
    obj = data["obj"]
    names = getRecent()
    for name in names:
        try:
            res = analysis_matches_by_name([name], dateRange, obj["q"], (obj["range"]["min"], obj["range"]["max"]), downloadRecordsFlag=False)
            await websocket.send_json({"status": 1, "data": res})
        except Exception as e:
            print(e)
            await websocket.send_json({"status": 0, "msg": "该比赛无法分析"})
    await websocket.close()


@app.post("/recommend")
async def analysis_matches(dateRange: str, obj: Analysis):
    dateRange = convertDateRange(dateRange)
    names = getRecent()
    allData = []
    for name in names:
        print(name)
        try:
            allData.append(analysis_matches_by_name([name], dateRange, obj.q, (obj.range.min, obj.range.max), downloadRecordsFlag=False))
        except ZeroDivisionError:
            pass
        except ValueError:
            pass
    return allData


if __name__ == "__main__":
    config = uvicorn.Config("main:app", port=5000, log_level="info", host="0.0.0.0")
    server = uvicorn.Server(config)
    server.run()
